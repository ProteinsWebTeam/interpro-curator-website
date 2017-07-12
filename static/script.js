$(function() {
    var updateEntrySection = function (data) {
        var pubIDs = [];
        var references = [];
        var description = data.description;
        var matches = description.match(/#(PUB\d+)/g);

        if (matches !== null) {
            matches.forEach(function (match) {
                var pubID = match.substr(1);
                var ref = data.references.hasOwnProperty(pubID) ? data.references[pubID] : null;
                var newSubstr;

                if (pubIDs.indexOf(pubID) === -1 && ref !== null) {
                    pubIDs.push(pubID);
                    references.push(ref);
                    newSubstr = '<a href="#'+ pubID +'">' + references.length + '</a>';
                } else
                    newSubstr = '';

                description = description.replace(new RegExp(match, 'g'), newSubstr);
            });
        }

        var regex = /\[XREF name="([^"]+)" url="([^"]*)"\]/g;
        var match = regex.exec(description);
        while (match !== null) {
            if (match[2].length)
                description = description.replace(match[0], '<a href="'+match[2]+'" target="_blank">' + match[1] + '&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a>');
            else
                description = description.replace(match[0], match[1]);

            match = regex.exec(description);
        }

        description = description.replace(/\[[^\]]+\]/g, '<sup>$&</sup>');

        var i;
        var n;
        var referencesHTML = '<ol>';

        for (i = 0, n = references.length; i < n; i++) {
            referencesHTML += '<li id="' + references[i].id + '">' +
                references[i].authors + ' ' +
                references[i].title + ' <i>' +
                references[i].journal + '</i> ' +
                references[i].year + ';' +
                references[i].volume + ':' +
                references[i].pages;

            referencesHTML += '<div class="level"><div class="level-left">';

            if (references[i].doi)
                referencesHTML += '<div class="level-item"><a href="' + references[i].doi + '" target="_blank">View article <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

            if (references[i].pmid)
                referencesHTML += '<div class="level-item"><a href="http://europepmc.org/abstract/MED/' + references[i].pmid + '" target="_blank">PubMed <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';


            referencesHTML += '</div></div></li>';
        }
        referencesHTML += '</ol>';

        var supReferencesHTML = '';
        var pubID;
        for (pubID in data.references) {
            if (data.references.hasOwnProperty(pubID) && pubIDs.indexOf(pubID) === -1) {
                supReferencesHTML += '<li id="' + data.references[pubID].id + '">' +
                    data.references[pubID].authors + ' ' +
                    data.references[pubID].title + ' <i>' +
                    data.references[pubID].journal + '</i> ' +
                    data.references[pubID].year + ';' +
                    data.references[pubID].volume + ':' +
                    data.references[pubID].pages;

                supReferencesHTML += '<div class="level"><div class="level-left">';

                if (data.references[pubID].doi)
                    supReferencesHTML += '<div class="level-item"><a href="' + data.references[pubID].doi + '" target="_blank">View article <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

                if (data.references[pubID].pmid)
                    supReferencesHTML += '<div class="level-item"><a href="http://europepmc.org/abstract/MED/' + data.references[pubID].pmid + '" target="_blank">PubMed <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';


                supReferencesHTML += '</div></div></li>';
            }
        }

        var goTerms = {
            'P': '',
            'F': '',
            'C': ''
        };

        data.go.forEach(function (term) {
            if (goTerms.hasOwnProperty(term.category))
                goTerms[term.category] += '<dd>' + '<a href="http://www.ebi.ac.uk/QuickGO/GTerm?id=' + term.id + '" target="_blank">' + term.id + ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a>&nbsp;' + term.name + '</dd>';
        });

        var goHTML = '<dl><dt>Biological Process</dt>' + (goTerms['P'].length ? goTerms['P'] : '<dd>No terms assigned in this category.</dd>');
        goHTML += '<dt>Molecular Function</dt>' + (goTerms['F'].length ? goTerms['F'] : '<dd>No terms assigned in this category.</dd>');
        goHTML += '<dt>Cellular Component</dt>' + (goTerms['C'].length ? goTerms['C'] : '<dd>No terms assigned in this category.</dd>') + '</dl>';

        var signaturesHTML = '';
        data.signatures.forEach(function (signature) {
            signaturesHTML += '<tr>';

            if (signature.home)
                signaturesHTML += '<td><a href="' + signature.home + '" target="_blank">' + signature.dbname + ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td>';
            else
                signaturesHTML += '<td>' + signature.dbname + '</td>';

            if (signature.link)
                signaturesHTML += '<td><a href="' + signature.link + '" target="_blank">' + signature.method_ac + ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td>';
            else
                signaturesHTML += '<td>' + signature.method_ac + '</td>';

            signaturesHTML += '<td>' + signature.name + '</td><td>' + signature.count + '</td>' +
                '<td><a href="http://www.ebi.ac.uk/internal-tools/openSQL/view,account:happy-helper-ippro-load/interpro/curation/OverlappingQuerySignature.jelly?signature=' + signature.method_ac + '" target="_blank">Happy Helper <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td></tr>';

            //
        });

        var relationshipsHTML = '';
        if (data.relationships.parents.length) {
            relationshipsHTML += '<dt>Parents</dt>';
            data.relationships.parents.forEach(function (entry) {
                relationshipsHTML += '<dd><a href="/'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (data.relationships.children.length) {
            relationshipsHTML += '<dt>Children</dt>';
            data.relationships.children.forEach(function (entry) {
                relationshipsHTML += '<dd><a href="/'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (data.relationships.containers.length) {
            relationshipsHTML += '<dt>Found in</dt>';
            data.relationships.containers.forEach(function (entry) {
                relationshipsHTML += '<dd><a href="/'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (data.relationships.components.length) {
            relationshipsHTML += '<dt>Contains</dt>';
            data.relationships.components.forEach(function (entry) {
                relationshipsHTML += '<dd><a href="/'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }

        document.getElementById('error').style.display = 'none';
        document.querySelector('#entry .title').innerHTML = data.id;
        document.querySelector('#entry .subtitle').innerHTML = data.name + ' (' + data.short_name + ')';

        document.getElementById('protein-count').innerHTML = data.count;
        document.getElementById('entry-type').innerHTML = data.type;
        document.getElementById('signature-count').innerHTML = data.signatures.length;
        document.getElementById('go-count').innerHTML = data.go.length;
        document.getElementById('reference-count').innerHTML = references.length;

        document.getElementById('description-content').innerHTML = description;
        document.getElementById('signatures-content').innerHTML = signaturesHTML;
        document.getElementById('relationships-content').innerHTML = relationshipsHTML.length ? '<dl>' + relationshipsHTML + '</dl>' : relationshipsHTML;
        document.getElementById('go-content').innerHTML = goHTML;
        document.getElementById('references-content').innerHTML = referencesHTML;

        if (supReferencesHTML.length)
            document.getElementById('suppl-references').innerHTML = '<p>The following publications were not referred to in the description, but provide useful additional information.</p><ul>' + supReferencesHTML + '</ul>';
        else
            document.getElementById('suppl-references').innerHTML = '<p>This entry has no additional references.</p>';

        if (data.warning !== null) {
            document.querySelector('#warning .message-body').innerHTML = data.warning;
            document.getElementById('warning').style.display = 'block';
        } else
            document.getElementById('warning').style.display = 'none';

        document.querySelectorAll('#curation-content a').forEach(function (el) {
            el.href = el.getAttribute('data-href') + data.id;
        });

        document.getElementById('entry').style.display = 'block';
    };

    var getEntry = function (searchQuery) {
        var loader = document.getElementById('loader');
        loader.className = 'modal is-active';

        $.getJSON($SCRIPT_ROOT + '/api/entry/' + searchQuery, function (data) {
            loader.className = 'modal';

            if (data.name === undefined || data.name === null) {
                document.getElementById('search-span').innerHTML = searchQuery;
                document.getElementById('error').style.display = 'block';
                document.getElementById('entry').style.display = 'none';
            } else
                updateEntrySection(data);

            $('#hero').animate({
                'min-height': null
            }, 'fast');
            document.getElementById('result').style.display = 'block';

        });
    };

    $('#search-input').keyup(function (e) {
        if (e.which === 13) {
            var value = this.value.trim();

            if (value.length)
                getEntry(value);
        }
    });

    $('#search-button').click(function () {
        var value = document.getElementById('search-input').value.trim();

        if (value.length)
            getEntry(value);
    });

    $('#menu').on('click', 'a', function () {
        document.querySelectorAll('#menu a').forEach( function (el) {
            el.className = '';
        });
        this.className = 'is-active';
    });

    if (entry !== null) {
        if (entry.name === undefined || entry.name === null) {
            document.getElementById('search-span').innerHTML = entryAc;
            document.getElementById('error').style.display = 'block';
            document.getElementById('entry').style.display = 'none';
        } else
            updateEntrySection(entry);

        $('#hero').animate({
            'min-height': null
        }, 'fast');
        document.getElementById('result').style.display = 'block';
    }
});