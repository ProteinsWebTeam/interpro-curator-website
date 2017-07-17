$(function() {
    var updateEntrySection = function (entry) {
        document.querySelector('#entry .title').innerHTML = entry.id;
        document.querySelector('#entry .subtitle').innerHTML = entry.name + ' (' + entry.short_name + ')';

        if (entry.missing_xref) {
            document.querySelector('#warning .message-header').innerHTML = "<p><strong>Hum. That's embarrassing</strong></p>";
            document.querySelector('#warning .message-body').innerHTML = '<p>At least one link for a cross-reference could not be generated. Please contact the production team.</p>';
            document.getElementById('warning').style.display = 'block';
        } else
            document.getElementById('warning').style.display = 'none';

        // Curation block
        document.querySelectorAll('#curation-content a').forEach(function (el) {
            el.href = el.getAttribute('data-href') + entry.id;
        });

        // Description block
        var description = entry.description;
        var references = entry.references;
        var orderedRefs = [];
        var re = /<cite id="([A-Z0-9,]+)"\/>/g;
        var arr;
        var content;
        while ((arr = re.exec(description)) !== null) {
            content = [];

            arr[1].split(',').forEach(function (refID) {
                if (references.hasOwnProperty(refID)) {
                    if (orderedRefs.indexOf(refID) === -1)
                        orderedRefs.push(refID);

                    content.push('<a href="#' + refID + '">' + orderedRefs.length + '</a>')
                }
            });

            description = description.replace(arr[0], '<sup>[' + content.join(', ') + ']</sup>');
        }

        re = /<xref name="([^"]+)" url="([^"]*)"\/>/g;
        while ((arr = re.exec(description)) !== null) {
            if (arr[2].length)
                description = description.replace(arr[0], '<a href="'+arr[2]+'" target="_blank">' + arr[1] + '&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a>');
            else
                description = description.replace(arr[0], arr[1]);
        }

        document.getElementById('description-content').innerHTML = description;

        // Header block (depends on references so not updated before)
        document.getElementById('protein-count').innerHTML = entry.count;
        document.getElementById('entry-type').innerHTML = entry.type.replace('_', ' ');
        document.getElementById('signature-count').innerHTML = entry.signatures.length;
        document.getElementById('go-count').innerHTML = entry.go.length;
        document.getElementById('reference-count').innerHTML = orderedRefs.length;

        // References block
        content = '';
        orderedRefs.forEach(function (refID) {
            var ref = references[refID];

            content += '<li id="' + ref.id + '">' + ref.authors + ' ' + ref.title + ' <i>' + ref.journal + '</i> ' +
                ref.year + ';' + ref.volume + ':' + ref.pages + '<div class="level"><div class="level-left">';

            if (ref.doi)
                content += '<div class="level-item"><a href="' + ref.doi + '" target="_blank">View article <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

            if (ref.pmid)
                content += '<div class="level-item"><a href="http://europepmc.org/abstract/MED/' + ref.pmid + '" target="_blank">Europe PMC <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

            content += '</div></div></li>';
        });

        document.getElementById('references-content').innerHTML = content.length ? '<ol>' + content + '</ol>' : '<p>This entry has no references.</p>';

        // Suppl. references block
        content = '';
        for (refID in references) {
            if (references.hasOwnProperty(refID) && orderedRefs.indexOf(refID) === -1) {
                content += '<li id="' + references[refID].id + '">' + references[refID].authors + ' ' +
                    references[refID].title + ' <i>' + references[refID].journal + '</i> ' +
                    references[refID].year + ';' + references[refID].volume + ':' + references[refID].pages +
                    '<div class="level"><div class="level-left">';

                if (references[refID].doi)
                    content += '<div class="level-item"><a href="' + references[refID].doi + '" target="_blank">View article <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

                if (references[refID].pmid)
                    content += '<div class="level-item"><a href="http://europepmc.org/abstract/MED/' + references[refID].pmid + '" target="_blank">Europe PMC <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

                content += '</div></div></li>';
            }
        }

        document.getElementById('suppl-references').innerHTML = content.length ? '<p>The following publications were not referred to in the description, but provide useful additional information.</p><ul>' + content + '</ul>' : '<p>This entry has no additional references.</p>';

        // Signatures table
        content = '';
        entry.signatures.forEach(function (s) {
            content += '<tr>';

            if (s.home)
                content += '<td><a href="' + s.home + '" target="_blank">' + s.dbname +
                    ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td>';
            else
                content += '<td>' + s.dbname + '</td>';

            if (s.link)
                content += '<td><a href="' + s.link + '" target="_blank">' + s.method_ac +
                    ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td>';
            else
                content += '<td>' + s.method_ac + '</td>';

            content += '<td>' + s.name + '</td><td>' + s.count + '</td>' +
                '<td><a href="http://www.ebi.ac.uk/internal-tools/openSQL/view,account:happy-helper-ippro-load/interpro/curation/OverlappingQuerySignature.jelly?signature=' +
                s.method_ac + '" target="_blank">Happy Helper <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></td></tr>';
        });

        document.getElementById('signatures-content').innerHTML = content;

        // Relationships block
        content = '';
        if (entry.relationships.parents.length) {
            content += '<dt>Parents</dt>';
            entry.relationships.parents.forEach(function (entry) {
                content += '<dd><a href="/entry/'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (entry.relationships.children.length) {
            content += '<dt>Children</dt>';
            entry.relationships.children.forEach(function (entry) {
                content += '<dd><a href="/entry'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (entry.relationships.containers.length) {
            content += '<dt>Found in</dt>';
            entry.relationships.containers.forEach(function (entry) {
                content += '<dd><a href="/entry'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }
        if (entry.relationships.components.length) {
            content += '<dt>Contains</dt>';
            entry.relationships.components.forEach(function (entry) {
                content += '<dd><a href="/entry'+ entry.ac +'">' + entry.ac + '</a>&nbsp;' + entry.name + '</dd>';
            });
        }

        document.getElementById('relationships-content').innerHTML = content.length ? '<dl>' + content + '</dl>' : '<p>This entry has no relationships (but do well on its own).</p>';

        // GO terms block
        var goTerms = {
            'P': '',
            'F': '',
            'C': ''
        };

        entry.go.forEach(function (term) {
            if (goTerms.hasOwnProperty(term.category))
                goTerms[term.category] += '<dd>' + '<a href="http://www.ebi.ac.uk/QuickGO/GTerm?id=' + term.id + '" target="_blank">' + term.id + ' <span class="icon is-small"><i class="fa fa-external-link"></i></span></a>&nbsp;' + term.name + '</dd>';
        });

        content = '<dl><dt>Biological Process</dt>' + (goTerms['P'].length ? goTerms['P'] : '<dd>No terms assigned in this category.</dd>');
        content += '<dt>Molecular Function</dt>' + (goTerms['F'].length ? goTerms['F'] : '<dd>No terms assigned in this category.</dd>');
        content += '<dt>Cellular Component</dt>' + (goTerms['C'].length ? goTerms['C'] : '<dd>No terms assigned in this category.</dd>') + '</dl>';
        document.getElementById('go-content').innerHTML = content;
    };

    var updateEntriesSection = function (entries) {
        var content = '';
        entries.forEach(function (entry) {
            content += '<tr><td><a href="/entry/' + entry.id + '">' + entry.id + '</a></td><td>' + entry.name + '</td><td>' + entry.type.replace('_', ' ') + '</td></tr>';
        });

        document.querySelector('#entries tbody').innerHTML = content;
    };

    var searchEntry = function (accession, url) {
        var loader = document.getElementById('loader');
        loader.className = 'modal is-active';

        $.getJSON($SCRIPT_ROOT + url + accession, function (data) {
            loader.className = 'modal';

            window.history.pushState(null, '', data.url);

            if (data.error !== undefined && data.error !== null) {
                document.querySelector('#error .message-header').innerHTML = '<p><strong>Keep on looking.</strong></p>';
                document.querySelector('#error .message-body').innerHTML = 'Your search for <strong>' + accession + '</strong> did not match any record in the database.';
                document.getElementById('error').style.display = 'block';
                document.getElementById('entry').style.display = 'none';
            } else {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'block';

                updateEntrySection(data.entry);
            }

            $('#hero').animate({
                'min-height': null
            }, 'fast');
        });
    };

    var searchText = function (text) {
        text = text.trim();
        var loader = document.getElementById('loader');
        loader.className = 'modal is-active';

        $.getJSON($SCRIPT_ROOT + '/api/search/', {q: text}, function (data) {
            loader.className = 'modal';

            if (data.url !== undefined && data.url !== null)
                window.history.pushState(null, '', data.url);

            if (data.error !== undefined && data.error !== null) {
                if (data.error === 'not_found') {
                    document.querySelector('#error .message-header').innerHTML = '<p><strong>Keep on looking.</strong></p>';
                    document.querySelector('#error .message-body').innerHTML = 'Your search for <strong>' + text + '</strong> did not match any record in the database.';
                }

                document.getElementById('error').style.display = 'block';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'none';
            } else if (data.type === 'entry') {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'block';
                document.getElementById('entries').style.display = 'none';
                updateEntrySection(data.entry);
            } else if (data.type === 'entries') {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'block';

                document.querySelector('#entries .title').innerHTML = 'Search results';
                document.querySelector('#entries .subtitle').innerHTML = data.entries.length + ' InterPro entries matching <strong>' + text + '</strong>';

                updateEntriesSection(data.entries);
            }

            $('#hero').animate({
                'min-height': null
            }, 'fast');
        });
    };

    $('#search-input').keyup(function (e) {
        if (e.which === 13) {
            var value = this.value.trim();

            if (value.length)
                searchText(value);
        }
    });

    $('#search-button').click(function () {
        var value = document.getElementById('search-input').value.trim();

        if (value.length)
            searchText(value);
    });

    $('#menu').on('click', 'a', function () {
        document.querySelectorAll('#menu a').forEach( function (el) {
            el.className = '';
        });
        this.className = 'is-active';
    });

    if (entryAc !== null)
        searchEntry(entryAc, '/api/entry/');
    else if (methodAc !== null)
        searchEntry(methodAc, '/api/signature/');
    else if (search !== null)
        searchText(search);
});