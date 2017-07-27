#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import cx_Oracle
from flask import Flask, g, jsonify, render_template, request


app = Flask(__name__)
app.config.from_object('config')

DATABASES = {
    # Method databases
    'B': {
        'name': 'SFLD',
        'home': 'http://sfld.rbvi.ucsf.edu/django/',
        'formatter': lambda ac: 'family/' + ac[5:] if ac.startwith('SFLDF') else 'superfamily/' + ac[5:] if ac.startwith('SFLDS') else 'subgroup/' + ac[5:],
        'link': 'http://sfld.rbvi.ucsf.edu/django/{}',
        'color': '#6175c3'
    },
    'D': {
        'name': 'ProDom',
        'home': 'http://prodom.prabi.fr/',
        'formatter': None,
        'link': 'http://prodom.prabi.fr/prodom/current/cgi-bin/request.pl?question=DBEN&query={}',
        'color': '#76b84a'
    },
    'F': {
        'name': 'PRINTS',
        'home': 'http://www.bioinf.manchester.ac.uk/dbbrowser/PRINTS/',
        'formatter': None,
        'link': 'http://www.bioinf.manchester.ac.uk/cgi-bin/dbbrowser/sprint/searchprintss.cgi?prints_accn={}&display_opts=Prints&category=None&queryform=false&regexpr=off',
        'color': '#6a863e'
    },
    'H': {
        'name': 'Pfam',
        'home': 'http://pfam.xfam.org/',
        'formatter': None,
        'link': 'http://pfam.xfam.org/family/{}',
        'color': '#a36b33'
    },
    'J': {
        'name': 'CDD',
        'home': 'http://www.ncbi.nlm.nih.gov/Structure/cdd/cdd.shtml',
        'formatter': None,
        'link': 'http://www.ncbi.nlm.nih.gov/Structure/cdd/cddsrv.cgi?uid={}',
        'color': '#a24863'
    },
    'M': {
        'name': 'PROSITE profiles',
        'home': 'http://prosite.expasy.org/',
        'formatter': None,
        'link': 'http://prosite.expasy.org/{}',
        'color': '#60a2d9'
    },
    'N': {
        'name': 'TIGRFAMs',
        'home': 'http://www.jcvi.org/cgi-bin/tigrfams/index.cgi',
        'formatter': None,
        'link': 'http://www.jcvi.org/cgi-bin/tigrfams/HmmReportPage.cgi?acc={}',
        'color': '#d18dcd'
    },
    'P': {
        'name': 'PROSITE patterns',
        'home': 'http://prosite.expasy.org/',
        'formatter': None,
        'link': 'http://prosite.expasy.org/{}',
        'color': '#4db395'
    },
    'Q': {
        'name': 'HAMAP',
        'home': 'http://hamap.expasy.org/',
        'formatter': None,
        'link': 'http://hamap.expasy.org/profile/{}',
        'color': '#e1827a'
    },
    'R': {
        'name': 'SMART',
        'home': 'http://smart.embl-heidelberg.de/',
        'formatter': None,
        'link': 'http://smart.embl-heidelberg.de/smart/do_annotation.pl?ACC={}&BLAST=DUMMY',
        'color': '#7e63d7'
    },
    'U': {
        'name': 'PIRSF',
        'home': 'http://pir.georgetown.edu/pirwww/dbinfo/pirsf.shtml',
        'formatter': None,
        'link': 'http://pir.georgetown.edu/cgi-bin/ipcSF?id={}',
        'color': '#d0a242'
    },
    'V': {
        'name': 'PANTHER',
        'home': 'http://www.pantherdb.org/',
        'formatter': None,
        'link': 'http://www.pantherdb.org/panther/family.do?clsAccession={}',
        'color': '#d04d33'
    },
    'X': {
        'name': 'CATH-Gene3D',
        'home': 'http://www.cathdb.info/',
        'formatter': lambda ac: re.match(r'G3DSA:(.+)', ac).group(1),
        'link': 'http://www.cathdb.info/superfamily/{}',
        'color': '#da467b'
    },
    'Y': {
        'name': 'SUPERFAMILY',
        'home': 'http://supfam.org/SUPERFAMILY/',
        'formatter': None,
        'link': 'http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid={}',
        'color': '#90519d'
    },
    'g': {
        'name': 'MobiDB Lite',
        'home': 'http://mobidb.bio.unipd.it/',
        'formatter': None,
        'link': 'http://mobidb.bio.unipd.it/entries/{}',
        'color': '#c952bc'
    },

    # Structural databases
    'A': {
        'name': 'MODBASE',
        'home': 'http://modbase.compbio.ucsf.edu/modbase-cgi/index.cgi',
        'formatter': lambda ac: re.match(r'MB_(.+)', ac).group(1),
        'link': 'http://modbase.compbio.ucsf.edu/modbase-cgi-new/model_search.cgi?searchvalue={}&searchproperties=database_id&displaymode=moddetail&searchmode=default',
        'color': '#1b9e77'
    },
    'b': {
        'name': 'PDB',
        'home': 'http://www.ebi.ac.uk/pdbe/',
        'formatter': None,
        'link': 'http://www.ebi.ac.uk/pdbe-srv/view/entry/{}/summary',
        'color': '#d95f02'
    },
    'h': {
        'name': 'CATH',
        'home': 'http://www.cathdb.info/',
        'formatter': None,
        'link': 'http://www.cathdb.info/superfamily/{}',
        'color': '#7570b3'
    },
    'W': {
        'name': 'SWISS-MODEL',
        'home': 'http://swissmodel.expasy.org/',
        'formatter': lambda ac: re.match(r'SW_(.+)', ac).group(1),
        'link': 'http://swissmodel.expasy.org/repository/?pid=smr03&query_1_input={}',
        'color': '#e7298a'
    },
    'y': {
        'name': 'SCOP',
        'home': 'http://scop.mrc-lmb.cam.ac.uk/scop',
        'formatter': None,
        'link': 'http://scop.mrc-lmb.cam.ac.uk/scop/search.cgi?key={}',
        'color': '#66a61e'
    },

}

XREF_DATABASES = {
    'CAZY': 'http://www.cazy.org/fam/{}.html',
    'EC': 'http://www.ebi.ac.uk/intenz/query?cmd=SearchEC&ec={}',
    'INTERPRO': '/entry/{}',
    'PROSITEDOC': 'http://www.expasy.org/cgi-bin/nicedoc.pl?{}',
    'SSF': 'http://supfam.org/SUPERFAMILY/cgi-bin/scop.cgi?ipid={}',
    'SWISSPROT': 'http://www.uniprot.org/uniprot/{}',
}


def connect_db():
    return cx_Oracle.connect(app.config['DATABASE'])


def open_db():
    if not hasattr(g, 'oracle_db'):
        g.oracle_db = connect_db()
    return g.oracle_db


def method_to_entry(method_ac):
    cur = open_db().cursor()
    cur.execute('SELECT E2M.ENTRY_AC '
                'FROM INTERPRO.METHOD M '
                'LEFT OUTER JOIN INTERPRO.ENTRY2METHOD E2M '
                'ON M.METHOD_AC=E2M.METHOD_AC '
                'WHERE M.METHOD_AC=:method_ac', method_ac=method_ac)

    row = cur.fetchone()
    return row[0] if row is not None else row


def get_entry(entry_ac):
    cur = open_db().cursor()
    cur.execute("SELECT "
                "  E.NAME, "
                "  E.SHORT_NAME, "
                "  ET.ABBREV, "
                "  E.CHECKED, "
                "  (SELECT COUNT(*) FROM INTERPRO.MV_ENTRY2PROTEIN MVEP WHERE MVEP.ENTRY_AC = :entry_ac),"
                "  E.CREATED,"
                "  E.TIMESTAMP "
                "FROM INTERPRO.ENTRY E "
                "INNER JOIN INTERPRO.CV_ENTRY_TYPE ET "
                "ON E.ENTRY_TYPE = ET.CODE "
                "LEFT OUTER JOIN INTERPRO.MV_ENTRY_MATCH EM ON E.ENTRY_AC = EM.ENTRY_AC "
                "WHERE E.ENTRY_AC = :entry_ac ", entry_ac=entry_ac)

    row = cur.fetchone()

    if not row:
        return None

    entry = {
        'id': entry_ac,
        'name': row[0],
        'short_name': row[1],
        'type': row[2],
        'checked': bool(row[3]),
        'count': row[4],
        'created': row[5].strftime('%Y-%m-%d %H:%M:%S'),
        'modified': row[6].strftime('%Y-%m-%d %H:%M:%S'),
        'signatures': [],
        'relationships': {
            'parents': [],
            'children': [],
            'containers': [],
            'components': [],
        },
        'go': [],
        'description': None,
        'references': None,
        'missing_xrefs': 0
    }

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

        if dbcode in DATABASES:
            db = DATABASES[dbcode]
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
    # cur.execute("SELECT G.GO_ID, G.CATEGORY, G.NAME "
    #             "FROM GO.TERMS@GOAPRO G "
    #             "INNER JOIN INTERPRO.INTERPRO2GO I2G ON G.GO_ID = I2G.GO_ID "
    #             "WHERE I2G.ENTRY_AC = :entry_ac "
    #             "ORDER BY G.CATEGORY, G.GO_ID", entry_ac=entry_ac)
    #
    # entry['go'] = [dict(zip(['id', 'category', 'name'], row)) for row in cur]

    cur.execute('SELECT DISTINCT GT.GO_ID, GT.CATEGORY, GT.NAME '
                'FROM GO.TERMS@GOAPRO GT '
                'INNER JOIN ('
                '  SELECT GS.GO_ID '
                '  FROM INTERPRO.INTERPRO2GO I2G '
                '  INNER JOIN GO.SECONDARIES@GOAPRO GS '
                '  ON I2G.GO_ID=GS.SECONDARY_ID '
                '  WHERE I2G.ENTRY_AC=:entry_ac '
                '  UNION '
                '  SELECT GT.GO_ID '
                '  FROM INTERPRO.INTERPRO2GO I2G '
                '  INNER JOIN GO.TERMS@GOAPRO GT '
                '  ON I2G.GO_ID=GT.GO_ID '
                '  WHERE I2G.ENTRY_AC=:entry_ac'
                ') GS '
                'ON GS.GO_ID = GT.GO_ID', entry_ac=entry_ac)

    entry['go'] = [dict(zip(['id', 'category', 'name'], row)) for row in cur]

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

    references = {row[0]: dict(zip(
        ['id', 'title', 'year', 'volume', 'pages', 'doi', 'pmid', 'journal', 'authors'],
        row
    )) for row in cur}

    # Description
    cur.execute("SELECT A.TEXT "
                "FROM INTERPRO.COMMON_ANNOTATION A "
                "INNER JOIN INTERPRO.ENTRY2COMMON E ON A.ANN_ID = E.ANN_ID "
                "WHERE E.ENTRY_AC = :entry_ac "
                "ORDER BY E.ORDER_IN", entry_ac=entry_ac)

    missing_references = []
    description = ''
    for row in cur:
        desc = row[0]

        if desc[:3].lower() != '<p>':
            desc = '<p>' + desc

        if desc[-4:].lower() != '</p>':
            desc += '</p>'

        # Find references and replace <cite id="PUBXXXX"/> by #PUBXXXX
        for m in re.finditer(r'<cite\s+id="(PUB\d+)"\s*/>', desc):
            ref = m.group(1)
            desc = desc.replace(m.group(0), '#' + ref)

            if ref not in references:
                missing_references.append(ref)

        for m in re.finditer(r'<dbxref\s+db="(\w+)"\s+id="([\w\.]+)"\s*\/>', desc):
            match = m.group(0)
            db = m.group(1)
            _id = m.group(2)

            if db in XREF_DATABASES:
                url = XREF_DATABASES[db].format(_id)
                xref = '<a href="{}">{}</a>'.format(url, _id)
            else:
                entry['missing_xrefs'] += 1
                xref = '<pre><xref name="{}" url=""/></pre>'.format(_id)

            desc = desc.replace(match, xref)

        for m in re.finditer(r'<taxon\s+tax_id="(\d+)">([^<]+)</taxon>', desc):
            match = m.group(0)
            tax_id = m.group(1)
            tax_name = m.group(2)
            desc = desc.replace(match, '<a href="http://www.uniprot.org/taxonomy/{}">{}</a>'.format(tax_id, tax_name))

        description += desc

    missing_references = list(set(missing_references))

    if missing_references:
        # For some entries, the association entry-citation is missing in the INTERPRO.ENTRY2PUB
        cur.execute(
            "SELECT "
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
            "WHERE C.PUB_ID IN ({})".format(','.join([':' + str(i+1) for i in range(len(missing_references))])),
            missing_references
        )

    references.update({row[0]: dict(zip(['id', 'title', 'year', 'volume', 'pages', 'doi', 'pmid', 'journal', 'authors'], row)) for row in cur})

    for block in re.findall(r'\[\s*#PUB\d+(?:\s*,\s*#PUB\d+)*\s*\]', description):
        refs = re.findall(r'#(PUB\d+)', block)

        description = description.replace(block, '<cite id="{}"/>'.format(','.join(refs)))

    entry['references'] = references
    entry['description'] = description

    return entry


def get_protein(protein_ac):
    cur = open_db().cursor()

    cur.execute('SELECT P.NAME, P.LEN, P.DBCODE, P.TAX_ID, E.SCIENTIFIC_NAME '
                'FROM INTERPRO.PROTEIN P '
                'LEFT OUTER JOIN INTERPRO.ETAXI E ON P.TAX_ID=E.TAX_ID '
                'WHERE PROTEIN_AC = :protein_ac', protein_ac=protein_ac)

    row = cur.fetchone()
    if not row:
        return None

    prot_name, prot_length, prot_db, prot_taxid, sci_name = row

    cur.execute(
        'SELECT E.ENTRY_AC, E.NAME, CET.ABBREV, MA.METHOD_AC, ME.NAME, MA.POS_FROM, MA.POS_TO, MA.DBCODE '
        'FROM INTERPRO.MATCH MA '
        'INNER JOIN INTERPRO.METHOD ME ON MA.METHOD_AC=ME.METHOD_AC '
        'LEFT OUTER JOIN INTERPRO.ENTRY2METHOD E2M ON E2M.METHOD_AC=MA.METHOD_AC '
        'LEFT OUTER JOIN INTERPRO.ENTRY E ON E2M.ENTRY_AC=E.ENTRY_AC '
        'LEFT OUTER JOIN INTERPRO.CV_ENTRY_TYPE CET ON CET.CODE=E.ENTRY_TYPE '
        'WHERE MA.PROTEIN_AC = :protein_ac',
        protein_ac=protein_ac
    )

    entries = {}
    for entry_ac, entry_name, entry_type, method_ac, method_name, pos_from, pos_to, dbcode in cur:
        if entry_ac not in entries:
            entries[entry_ac] = dict(
                id=entry_ac,
                name=entry_name,
                type=entry_type,
                signatures=dict()
            )

        if method_ac not in entries[entry_ac]['signatures']:
            db = DATABASES[dbcode]

            entries[entry_ac]['signatures'][method_ac] = dict(
                id=method_ac,
                name=method_name,
                db=db['name'],
                color=db['color'],
                url=db['link'].format(db['formatter'](method_ac) if db['formatter'] else method_ac),
                matches=[]
            )

        entries[entry_ac]['signatures'][method_ac]['matches'].append({'from': pos_from, 'to': pos_to})

    for entry_ac, entry in entries.items():
        entry['signatures'] = sorted(entry['signatures'].values(), key=lambda x: x['id'])

    # Structural features and predictions
    cur.execute('SELECT MS.DBCODE, MS.DOMAIN_ID, SC.FAM_ID, MS.POS_FROM, MS.POS_TO '
                'FROM INTERPRO.MATCH_STRUCT MS '
                'INNER JOIN INTERPRO.STRUCT_CLASS SC ON MS.DOMAIN_ID=SC.DOMAIN_ID '
                'WHERE MS.PROTEIN_AC=:protein_ac', protein_ac=protein_ac)

    methods = {}
    for dbcode, domain_id, fam_id, pos_from, pos_to in cur:
        db = DATABASES[dbcode]

        if dbcode not in methods:
            methods[dbcode] = dict(
                name=db['name'],
                url=db['home'],
                color=db['color'],
                matches=[]
            )

        methods[dbcode]['matches'].append({
            'id': fam_id,
            'url': db['link'].format(db['formatter'](fam_id) if db['formatter'] else fam_id),
            'from': pos_from,
            'to': pos_to
        })

    return dict(
        id=protein_ac,
        name=prot_name,
        length=prot_length,
        db=prot_db,
        organism=sci_name,
        prot_taxid=prot_taxid,
        entries=sorted(
            entries.values(),
            # Families, Domains, and Repeats come first, None (Unintegrated) come last
            key=lambda x: {'Family': 0, 'Domain': 1, 'Repeat': 2, None: 99}.get(x['type'], 50)
        ),
        structs=sorted(methods.values(), key=lambda x: x['name'])
    )


def is_protein(protein_ac):
    cur = open_db().cursor()
    cur.execute('SELECT P.PROTEIN_AC '
                'FROM INTERPRO.PROTEIN P '
                'WHERE P.PROTEIN_AC = :protein_ac', protein_ac=protein_ac)

    row = cur.fetchone()
    return row[0] if row else None


def search_entries(terms, fields=['abstract', 'common', 'entry', 'go', 'method', 'publication', 'xref']):
    cur = open_db().cursor()

    params = {}
    field_cond = []
    for i, field in enumerate(fields):
        key = 'field_' + str(i + 1)
        field_cond.append(':' + key)
        params[key] = field.lower()

    term_cond = []
    for i, term in enumerate(terms):
        key = 'term_' + str(i + 1)
        term_cond.append('TEXT = :' + key)
        params[key] = term.upper()

    params['nterms'] = len(terms)

    cur.execute(
        'SELECT E.ENTRY_AC, E.NAME, ET.ABBREV '
        'FROM INTERPRO.ENTRY E, ('
        '  SELECT SQ.ID, SUM(SQ.CNT) CNT FROM ('
        '    SELECT ID, TEXT, COUNT(*) CNT '
        '    FROM INTERPRO.TEXT_INDEX_ENTRY '
        '    WHERE FIELD IN ({}) AND ({}) '
        '    GROUP BY ID, TEXT'
        '  ) SQ '
        '  GROUP BY SQ.ID '
        '  HAVING COUNT(*) = :nterms'
        ') S, '
        'INTERPRO.CV_ENTRY_TYPE ET '
        'WHERE E.ENTRY_AC = S.ID AND E.ENTRY_TYPE = ET.CODE '
        'ORDER BY S.CNT DESC, E.ENTRY_AC ASC'.format(
            ','.join(field_cond),
            ' OR '.join(term_cond)
        ), params)

    return cur.fetchall()


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


@app.route('/entry/<entry_ac>/')
def entry_page(entry_ac):
    return render_template('index.html', entry_ac=entry_ac)


@app.route('/signature/<method_ac>/')
def signature_page(method_ac):
    return render_template('index.html', method_ac=method_ac)

@app.route('/protein/<protein_ac>/')
def protein_page(protein_ac):
    return render_template('index.html', protein_ac=protein_ac)


@app.route('/search/')
def search_page():
    text = request.args.get('q', '').strip().strip('"\'')
    return render_template('index.html', search=text)


@app.route('/api/')
def api_root():
    return "Ain't nobody here but us chickens"


@app.route('/api/search/')
def api_search():
    text = request.args.get('q', '').strip().strip('"\'')
    m = re.match(r'(?:IPR)?(\d+)$', text, re.I)

    if m:
        entry_ac = 'IPR{:06d}'.format(int(m.group(1)))
        try:
            entry = get_entry(entry_ac)
        except:
            return jsonify(dict(
                error=dict(
                    title='There is a fly in the ointment!',
                    message='Something went wrong when searching for <strong>{}</strong>. Contact the production team.'.format(entry_ac)
                )
            ))

        if entry:
            return jsonify(dict(
                type='entry',
                url='/entry/' + entry['id'],
                entry=entry
            ))

    entry_ac = method_to_entry(text)
    if entry_ac:
        try:
            entry = get_entry(entry_ac)
        except:
            return jsonify(dict(
                error=dict(
                    title='There is a fly in the ointment!',
                    message='Something went wrong when searching for <strong>{}</strong>. Contact the production team.'.format(text)
                )
            ))

        return jsonify(dict(
            type='entry',
            url='/signature/' + text,
            entry=entry
        ))

    try:
        protein = get_protein(text)
    except Exception as e:
        return jsonify(dict(
            error=dict(
                title='There is a fly in the ointment!',
                message='Something went wrong when searching for <strong>{}</strong>. Contact the production team.'.format(text)
            )
        ))
    if protein:
        return jsonify(dict(
            type='protein',
            url='/protein/' + text,
            protein=protein
        ))

    entries = search_entries(text.split())
    if entries:
        return jsonify(dict(
            type='entries',
            url='/search?q="{}"'.format(text),
            entries=[dict(zip(['id', 'name', 'type'], e)) for e in entries]
        ))

    return jsonify(dict(
        error=dict(
            title='Keep on looking',
            message='Your search for <strong>{}</strong> did not match any record in the database.'.format(text)
        )
    ))


@app.route('/api/entry/<entry_ac>/')
def api_entry(entry_ac):
    m = re.match(r'(?:IPR)?(\d+)$', entry_ac, re.I)

    if m:
        entry = get_entry('IPR{:06d}'.format(int(m.group(1))))
    else:
        entry = None

    if entry:
        return jsonify(dict(
            type='entry',
            entry=entry,
            url='/entry/' + entry['id']
        ))
    else:
        return jsonify(dict(
            error=dict(
                title='Keep on looking',
                message='Your search for <strong>{}</strong> did not match any record in the database.'.format(entry_ac)
            ),
            url='/entry/' + entry_ac
        ))


@app.route('/api/signature/<method_ac>/')
def api_signature(method_ac):
    entry_ac = method_to_entry(method_ac)
    if entry_ac:
        entry = get_entry(entry_ac)
        return jsonify(dict(
            type='entry',
            entry=entry,
            url='/signature/' + method_ac
        ))
    else:
        return jsonify(dict(
            error=dict(
                title='Keep on looking',
                message='Your search for <strong>{}</strong> did not match any record in the database.'.format(method_ac)
            ),
            url='/signature/' + method_ac
        ))


@app.route('/api/protein/<protein_ac>/')
def api_protein(protein_ac):
    protein = get_protein(protein_ac)

    if protein:
        return jsonify(dict(
            type='protein',
            url='/protein/' + protein_ac,
            protein=protein
        ))
    else:
        return jsonify(dict(
            error=dict(
                title='Keep on looking',
                message='Your search for <strong>{}</strong> did not match any record in the database.'.format(protein_ac)
            ),
            url='/protein/' + protein_ac
        ))


if __name__ == '__main__':
    app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
