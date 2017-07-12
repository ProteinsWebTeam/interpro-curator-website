#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import cx_Oracle
from flask import Flask, g, jsonify, render_template


app = Flask(__name__)
app.config.from_object('config')

MEMBER_DATABASES = {
    'X': {
        'name': 'CATH-Gene3D',
        'home': 'http://www.cathdb.info/',
        'formatter': lambda ac: re.match(r'G3DSA:(.+)', ac).group(1),
        'link': 'http://www.cathdb.info/superfamily/{}'
    },
    'J': {
        'name': 'CDD',
        'home': 'http://www.ncbi.nlm.nih.gov/Structure/cdd/cdd.shtml',
        'formatter': None,
        'link': 'http://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid={}'
    },
    'Q': {
        'name': 'HAMAP',
        'home': 'http://hamap.expasy.org/',
        'formatter': None,
        'link': 'http://hamap.expasy.org/profile/{}'
    },
    'V': {
        'name': 'PANTHER',
        'home': 'http://www.pantherdb.org/',
        'formatter': None,
        'link': 'http://www.pantherdb.org/panther/family.do?clsAccession={}'
    },
    'H': {
        'name': 'Pfam',
        'home': 'http://pfam.xfam.org/',
        'formatter': None,
        'link': 'http://pfam.xfam.org/family/{}'
    },
    'U': {
        'name': 'PIRSF',
        'home': 'http://pir.georgetown.edu/pirwww/dbinfo/pirsf.shtml',
        'formatter': None,
        'link': 'http://pir.georgetown.edu/cgi-bin/ipcSF?id={}'
    },
    'F': {
        'name': 'PRINTS',
        'home': 'http://www.bioinf.manchester.ac.uk/dbbrowser/PRINTS/',
        'formatter': None,
        'link': 'http://www.bioinf.manchester.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?prints_accn={}&display_opts=Prints&category=None&queryform=false&regexpr=off'
    },
    'D': {
        'name': 'ProDom',
        'home': 'http://prodom.prabi.fr/',
        'formatter': None,
        'link': 'http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&query={}'
    },
    'P': {
        'name': 'PROSITE patterns',
        'home': 'http://prosite.expasy.org/',
        'formatter': None,
        'link': 'http://prosite.expasy.org/{}'
    },
    'M': {
        'name': 'PROSITE profiles',
        'home': 'http://prosite.expasy.org/',
        'formatter': None,
        'link': 'http://prosite.expasy.org/{}'
    },
    'B': {
        'name': 'SFLD',
        'home': 'http://sfld.rbvi.ucsf.edu/django/',
        'formatter': lambda ac: 'family/' + ac[5:] if ac.startwith('SFLDF') else 'superfamily/' + ac[5:] if ac.startwith('SFLDS') else 'subgroup/' + ac[5:],
        'link': 'http://sfld.rbvi.ucsf.edu/django/{}'
    },
    'R': {
        'name': 'SMART',
        'home': 'http://smart.embl-heidelberg.de/',
        'formatter': None,
        'link': 'http://smart.embl-heidelberg.de/smart/do_annotation.pl?ACC={}&BLAST=DUMMY'
    },
    'Y': {
        'name': 'SUPERFAMILY',
        'home': 'http://supfam.org/SUPERFAMILY/',
        'formatter': None,
        'link': 'http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid={}'
    },
    'N': {
        'name': 'TIGRFAMs',
        'home': 'http://www.jcvi.org/cgi-bin/tigrfams/index.cgi',
        'formatter': None,
        'link': 'http://www.jcvi.org/cgi-bin/tigrfams/HmmReportPage.cgi?acc={}'
    },
}

XREF_DATABASES = {
    'EC': 'http://www.ebi.ac.uk/intenz/query?cmd=SearchEC&ec={}',
    'INTERPRO': '/{}'
}


def connect_db():
    return cx_Oracle.connect(app.config['DATABASE'])


def open_db():
    if not hasattr(g, 'oracle_db'):
        g.oracle_db = connect_db()
    return g.oracle_db


def get_entry(entry_ac):
    entry = {
        'id': None,
        'name': None,
        'short_name': None,
        'type': None,
        'checked': None,
        'count': None,
        'created': None,
        'modified': None,
        'signatures': [],
        'relationships': {
            'parents': [],
            'children': [],
            'containers': [],
            'components': [],
        },
        'go': [],
        'description': '',
        'references': [],
        'warning': None
    }

    cur = open_db().cursor()
    cur.execute("SELECT "
                "  E.NAME, "
                "  E.SHORT_NAME, "
                "  ET.ABBREV, "
                "  E.CHECKED, "
                "  (SELECT COUNT(*) FROM INTERPRO.MV_ENTRY2PROTEIN_TRUE MVEP WHERE MVEP.ENTRY_AC = :entry_ac),"
                "  E.CREATED,"
                "  E.TIMESTAMP "
                "FROM INTERPRO.ENTRY E "
                "INNER JOIN INTERPRO.CV_ENTRY_TYPE ET "
                "ON E.ENTRY_TYPE = ET.CODE "
                "LEFT OUTER JOIN INTERPRO.MV_ENTRY_MATCH EM ON E.ENTRY_AC = EM.ENTRY_AC "
                "WHERE E.ENTRY_AC = :entry_ac ", entry_ac=entry_ac)

    row = cur.fetchone()

    if row:
        entry['id'] = entry_ac
        entry['name'] = row[0]
        entry['short_name'] = row[1]
        entry['type'] = row[2]
        entry['checked'] = bool(row[3])
        entry['count'] = row[4]
        entry['created'] = row[5].strftime('%Y-%m-%d %H:%M:%S')
        entry['modified'] = row[6].strftime('%Y-%m-%d %H:%M:%S')

        # Signature
        cur.execute("SELECT M.DBCODE, M.METHOD_AC, M.NAME, NVL(MM.PROTEIN_COUNT, 0) "
                    "FROM INTERPRO.METHOD M "
                    "INNER JOIN INTERPRO.ENTRY2METHOD E2M ON M.METHOD_AC = E2M.METHOD_AC "
                    "RIGHT OUTER JOIN INTERPRO.MV_METHOD_MATCH MM ON M.METHOD_AC = MM.METHOD_AC "
                    "WHERE E2M.ENTRY_AC = :entry_ac ORDER BY M.METHOD_AC", entry_ac=entry_ac)

        for row in cur:
            dbcode = row[0]
            method_ac = row[1]
            name = row[2]
            count = row[3]

            dbname = None
            home = None
            link = None

            if dbcode in MEMBER_DATABASES:
                db = MEMBER_DATABASES[dbcode]
                dbname = db['name']
                home = db['home']

                if db['formatter'] is None:
                    link = db['link'].format(method_ac)
                else:
                    link = db['link'].format(db['formatter'](method_ac))

            entry['signatures'].append({
                'dbname': dbname,
                'home': home,
                'link': link,
                'method_ac': method_ac,
                'name': name,
                'count': count
            })

        # Relationships
        # Parents
        cur.execute("SELECT E.ENTRY_AC, E.NAME, E.CHECKED "
                    "FROM INTERPRO.ENTRY E "
                    "INNER JOIN INTERPRO.ENTRY2ENTRY EE "
                    "ON EE.PARENT_AC = E.ENTRY_AC "
                    "WHERE EE.ENTRY_AC = :entry_ac", entry_ac=entry_ac)

        for row in cur:
            entry['relationships']['parents'].append({
                'ac': row[0],
                'name': row[1],
                'checked': bool(row[2])
            })

        # Children
        cur.execute("SELECT E.ENTRY_AC, E.NAME, E.CHECKED "
                    "FROM INTERPRO.ENTRY E "
                    "INNER JOIN INTERPRO.ENTRY2ENTRY EE "
                    "ON EE.ENTRY_AC = E.ENTRY_AC "
                    "WHERE EE.PARENT_AC = :entry_ac", entry_ac=entry_ac)

        for row in cur:
            entry['relationships']['children'].append({
                'ac': row[0],
                'name': row[1],
                'checked': bool(row[2])
            })

        # Containers
        cur.execute("SELECT E.ENTRY_AC, E.NAME, E.CHECKED "
                    "FROM INTERPRO.ENTRY E "
                    "INNER JOIN INTERPRO.ENTRY2COMP EC "
                    "ON EC.ENTRY1_AC = E.ENTRY_AC "
                    "WHERE EC.ENTRY2_AC = :entry_ac", entry_ac=entry_ac)

        for row in cur:
            entry['relationships']['containers'].append({
                'ac': row[0],
                'name': row[1],
                'checked': bool(row[2])
            })

        # Components
        cur.execute("SELECT E.ENTRY_AC, E.NAME, E.CHECKED "
                    "FROM INTERPRO.ENTRY E "
                    "INNER JOIN INTERPRO.ENTRY2COMP EC "
                    "ON EC.ENTRY2_AC = E.ENTRY_AC "
                    "WHERE EC.ENTRY1_AC = :entry_ac", entry_ac=entry_ac)

        for row in cur:
            entry['relationships']['components'].append({
                'ac': row[0],
                'name': row[1],
                'checked': bool(row[2])
            })

        # GO annotations
        cur.execute("SELECT G.CATEGORY, G.GO_ID, G.NAME "
                    "FROM GO.TERMS@GOAPRO G "
                    "INNER JOIN INTERPRO.INTERPRO2GO I2G ON G.GO_ID = I2G.GO_ID "
                    "WHERE I2G.ENTRY_AC = :entry_ac "
                    "ORDER BY G.CATEGORY, G.GO_ID", entry_ac=entry_ac)

        entry['go'] = [dict(zip(['category', 'id', 'name'], row)) for row in cur]

        # References
        cur.execute("SELECT "
                    "  DISTINCT(C.PUB_ID), "
                    "  C.TITLE, "
                    "  C.YEAR, "
                    "  C.VOLUME, "
                    "  C.RAWPAGES, "
                    "  C.DOI_URL, "
                    "  C.PUBMED_ID, "
                    "  C.ISO_JOURNAL, "
                    "  C.AUTHORS "
                    "FROM INTERPRO.CITATION C "
                    "WHERE C.PUB_ID IN ("
                    "  SELECT E2P.PUB_ID "
                    "  FROM INTERPRO.ENTRY2PUB E2P "
                    "  WHERE E2P.ENTRY_AC = :entry_ac "
                    "  UNION "
                    "  SELECT M.PUB_ID "
                    "  FROM INTERPRO.METHOD2PUB M, INTERPRO.ENTRY2METHOD E "
                    "  WHERE E.ENTRY_AC = :entry_ac AND E.METHOD_AC = M.METHOD_AC "
                    "  UNION "
                    "  SELECT PDB.PUB_ID "
                    "  FROM INTERPRO.PDB_PUB_ADDITIONAL PDB "
                    "  WHERE PDB.ENTRY_AC = :entry_ac"
                    ")", entry_ac=entry_ac)

        cols = ['id', 'title', 'year', 'volume', 'pages', 'doi', 'pmid', 'journal', 'authors']
        entry['references'] = {row[0]: dict(zip(cols, row)) for row in cur}

        # Description
        cur.execute("SELECT A.TEXT "
                    "FROM INTERPRO.COMMON_ANNOTATION A "
                    "INNER JOIN INTERPRO.ENTRY2COMMON E ON A.ANN_ID = E.ANN_ID "
                    "WHERE E.ENTRY_AC = :entry_ac "
                    "ORDER BY E.ORDER_IN", entry_ac=entry_ac)

        for row in cur:
            # Trim paragraph tags (<p>, </p>)
            desc = row[0].lstrip('<p>').rstrip('</p>')

            # Add back tags
            desc = '<p>' + desc + '</p>'

            # Remove \r and \n
            for c in ['\r', '\n']:
                desc = desc.replace(c, '')

            # Replace <cite id="PUBXXXX"/> by #PUBXXXX
            desc = re.sub(r'<cite id="(PUB\d+)"/>', '#\\1', desc)

            for m in re.finditer(r'<dbxref db="(\w+)" id="([\w\.]+)"\/>', desc):
                match = m.group(0)
                db = m.group(1)
                _id = m.group(2)

                if db in XREF_DATABASES:
                    url = XREF_DATABASES[db].format(_id)
                    xref = '[XREF name="{}" url="{}"]'.format(_id, url)
                else:
                    xref = '[XREF name="{}" url=""]'.format(_id)
                    entry['warning'] = ('At least one link for a cross-reference could not be generated. '
                                        'Please contact the production team.')

                desc = desc.replace(match, xref)

            entry['description'] += desc

    return entry


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'oracle_db'):
        g.oracle_db.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<entry_ac>/')
def entry_page(entry_ac):
    m = re.match(r'(?:IPR)?(\d+)$', entry_ac, re.I)

    if m:
        entry_ac = 'IPR{:06d}'.format(int(m.group(1)))

    return render_template('index.html', entry=get_entry(entry_ac), ac=entry_ac)


@app.route('/api/')
def api_root():
    return "Ain't nobody here but us chickens"


@app.route('/api/entry/<entry_ac>/')
def api_entry(entry_ac):
    m = re.match(r'(?:IPR)?(\d+)$', entry_ac, re.I)

    if m:
        entry_ac = 'IPR{:06d}'.format(int(m.group(1)))

    return jsonify(get_entry(entry_ac))


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
