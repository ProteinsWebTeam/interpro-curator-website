$(function() {
    var tooltip = {
        el: $('#tooltip'),
        active: false,

        show: function (rect) {
            this.el.css({
                top: rect.top - this.el.outerHeight() - 5 + $(document).scrollTop(),
                left: rect.left + rect.width / 2 - this.el.outerWidth() / 2
            }).show();
            this.active = true;
        },

        _hide: function () {
            if (!this.active)
                this.el.hide();
        },

        hide: function () {
            this.active = false;
            var self = this;
            setTimeout(function () {
                self._hide();
            }, 500);
        },

        update: function (fromPos, toPos, sId, sName, sURL, dbName) {
            var $p = this.el.find('p');
            $p.get(0).innerHTML = fromPos.toLocaleString() + ' - ' + toPos.toLocaleString();
            $p.get(1).innerHTML = sName;
            $p.get(2).innerHTML = '<strong>' + dbName + '</strong> <a target="_blank" href="'+ sURL +'">'+ sId +'&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a>';
        },

        init: function () {
            var self = this;
            this.el.on('mouseenter', function () {
                self.active = true;
            });

            this.el.on('mouseleave', function () {
                self.hide();
            });
        }
    };

    tooltip.init();

    var updateEntrySection = function (entry) {
        document.querySelector('#entry .title').innerHTML = entry.id;
        document.querySelector('#entry .subtitle').innerHTML = entry.name + ' (' + entry.short_name + ')';

        if (entry.missing_xrefs) {
            document.querySelector('#warning .message-header').innerHTML = "<p><strong>Hum. That's embarrassing</strong></p>";
            document.querySelector('#warning .message-body').innerHTML = '<p>At least one link for a cross-reference could not be generated. Please contact the production team.</p>';
            document.getElementById('warning').style.display = 'block';
        } else
            document.getElementById('warning').style.display = 'none';

        // Curation block
        document.querySelectorAll('#curation-content a[data-href-entry]').forEach(function (el) {
            el.href = el.getAttribute('data-href-entry') + entry.id;
        });

        document.querySelectorAll('#curation-content a[data-href-signatures]').forEach(function (el) {
            var signatures = [];
            entry.signatures.forEach(function (s) {
                signatures.push(s.method_ac);
            });

            el.href = el.getAttribute('data-href-signatures') + signatures.join(',');
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

        document.getElementById('description-content').innerHTML = description;

        // Header block (depends on references so not updated before)
        document.getElementById('protein-count').innerHTML = entry.count.toLocaleString();
        document.getElementById('entry-type').innerHTML = entry.type.replace('_', ' ');
        document.getElementById('signature-count').innerHTML = entry.signatures.length;
        document.getElementById('go-count').innerHTML = entry.go.length;
        document.getElementById('reference-count').innerHTML = orderedRefs.length;

        // References block
        content = '';
        orderedRefs.forEach(function (refID) {
            var ref = references[refID];

            content += '<li id="' + ref.id + '">' + ref.authors + ' ' + ref.title + ' <i>' + ref.journal + '</i> ' +
                ref.year + ';' + ref.volume + ':' + ref.pages;

            if (ref.doi || ref.pmid) {
                content += '<div class="level"><div class="level-left">';

                if (ref.doi)
                    content += '<div class="level-item"><a href="' + ref.doi + '" target="_blank">View article <span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

                if (ref.pmid)
                    content += '<div class="level-item">PMID:&nbsp;<a href="http://europepmc.org/abstract/MED/' + ref.pmid + '" target="_blank">'+ ref.pmid +'&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

                content += '</div></div>';
            }

            content += '</li>';
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
                    content += '<div class="level-item">PMID:&nbsp;<a href="http://europepmc.org/abstract/MED/' + references[refID].pmid + '" target="_blank">' + references[refID].pmid + '&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a></div>';

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

            content += '<td>' + s.name + '</td><td>' + s.count.toLocaleString() + '</td>' +
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
                goTerms[term.category] += '<dd>' + '<a href="http://www.ebi.ac.uk/QuickGO/GTerm?id=' + term.id + '" target="_blank">' + term.id + '&nbsp;<span class="icon is-small"><i class="fa fa-external-link"></i></span></a>&nbsp;' + term.name + '</dd>';
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

    var updateProteinMatchesSection = function (protein) {
        document.getElementById('protein-id').innerHTML = '<a href="http://www.uniprot.org/uniprot/'+ protein.id +'" target="_blank">' + protein.id + '&nbsp;<span class="icon"><i class="fa fa-external-link"></i></span></a>';
        document.getElementById('protein-name').innerHTML = protein.name;
        document.getElementById('protein-organism').innerHTML = protein.organism !== null && protein.organism.length > 30 ? '<abbr title="'+protein.organism+'">'+protein.organism.substr(0, 30)+'&hellip;</abbr>': protein.organism;
        document.getElementById('protein-length').innerHTML = protein.length.toLocaleString();

        var $el = $('#matches');
        var content = '';
        var fullWidth = $el.width();
        var width = fullWidth - 200;
        var step = Math.pow(10, Math.floor(Math.log(protein.length) / Math.log(10))) / 2;

        protein.entries.forEach(function (entry) {
            content += '';

            if (entry.id !== null)
                content += '<p><a href="/entry/'+ entry.id +'">' + entry.id + '</a>&nbsp;' + entry.name + '</p>';
            else
                content += '<p>Unintegrated signatures</p>';

            var svgHeight = (15 * (entry.signatures.length + 1) + 5);
            var svgContent = 15 * entry.signatures.length + 5;

            content += '<svg width="' + fullWidth + '" height="'+ svgHeight +'" xmlns="http://www.w3.org/2000/svg"><rect height="' + svgContent + '" width="'+ width +'" fill="#eee"></rect>';

            var pos;
            var x;
            content += '<g class="ticks">';
            for (pos = step; pos < protein.length; pos += step) {
                x = pos * width / protein.length;
                content += '<line stroke-dasharray="2, 2" x1="'+ x +'" y1="0" x2="'+ x +'" y2="'+svgContent+'" stroke="black" stroke-width="0.5" />';
                content += '<text x="' + x + '" y="'+ svgContent +'">' + pos.toLocaleString() + '</text>';
            }
            content += '</g>';

            entry.signatures.forEach(function (s, i) {
                var color = s.color !== undefined && s.color !== null ? s.color : '#a5a5a5';
                var y = 5 + i * 15;

                content += '<g data-id="'+ s.id +'" data-name="'+ s.name +'" data-db="'+ s.db +'" data-url="'+ s.url +'">';

                s.matches.forEach(function (m) {
                    var x = m.from * width / protein.length;
                    var rectWidth = (m.to * width / protein.length) - x;
                    content += '<rect data-from="' + m.from + '" data-to="' + m.to + '" x="' + x + '" y="' + y + '" width="'+ rectWidth +'" height="10" rx="2" ry="2" fill="' + color + '"></rect>';
                });

                content += '<text x="' + (width + 10) + '" y="' + (y + 5) + '"><a target="_blank" href="'+s.url+'">' + s.id + '&nbsp;<tspan>&#xf08e;</tspan></a></text></g>';
            });

            content += '</svg>';
        });

        $el
            .html(content)
            .off()
            .on('mouseenter', 'rect[data-from]', function () {
                var $g = $(this).parent();

                var fromPos = $(this).data('from');
                var toPos = $(this).data('to');
                var sID = $g.data('id');
                var sName = $g.data('name');
                var sURL = $g.data('url');
                var dbName = $g.data('db');

                tooltip.update(fromPos, toPos, sID, sName, sURL, dbName);
                tooltip.show(this.getBoundingClientRect());
            })
            .on('mouseleave', 'rect[data-from]', function () {
                tooltip.hide();
            });

        var svgHeight = (15 * (protein.structs.length + 1) + 5);
        var svgContent = 15 * protein.structs.length + 5;
        content = '<svg width="' + fullWidth + '" height="'+ svgHeight +'" xmlns="http://www.w3.org/2000/svg"><rect height="' + svgContent + '" width="'+ width +'" fill="#eee"></rect>';

        var x;
        var pos;
        content += '<g class="ticks">';
        for (pos = step; pos < protein.length; pos += step) {
            x = pos * width / protein.length;
            content += '<line stroke-dasharray="2, 2" x1="'+ x +'" y1="0" x2="'+ x +'" y2="'+svgContent+'" stroke="black" stroke-width="0.5" />';
            content += '<text x="' + x + '" y="'+ svgContent +'">' + pos.toLocaleString() + '</text>';
        }
        content += '</g>';

        protein.structs.forEach(function (db, i, arr) {
            content += '';
            var color = db.color !== undefined && db.color !== null ? db.color : '#a5a5a5';
            var y = 5 + i * 15;

            content += '<g data-db="'+ db.name +'">';

            db.matches.forEach(function (m) {
                var x = m.from * width / protein.length;
                var rectWidth = (m.to * width / protein.length) - x;
                content += '<rect data-from="' + m.from + '" data-to="' + m.to + '" data-id="'+m.id+'" data-url="'+m.url+'" x="' + x + '" y="' + y + '" width="'+ rectWidth +'" height="10" rx="2" ry="2" fill="' + color + '"></rect>';
            });

            content += '<text x="' + (width + 10) + '" y="' + (y + 5) + '"><a target="_blank" href="'+db.url+'">' + db.name + '&nbsp;<tspan>&#xf08e;</tspan></a></text></g>';
        });

        content += '</svg>';

        $('#struct-matches')
            .html(protein.structs.length ? content : '<p>No structural match data for this protein.</p>')
            .off()
            .on('mouseenter', 'rect[data-from]', function () {
                var $g = $(this).parent();

                var fromPos = $(this).data('from');
                var toPos = $(this).data('to');
                var mID = $(this).data('id');
                var mURL = $(this).data('url');
                var dbName = $g.data('db');

                tooltip.update(fromPos, toPos, mID, '', mURL, dbName);
                tooltip.show(this.getBoundingClientRect());
            })
            .on('mouseleave', 'rect[data-from]', function () {
                tooltip.hide();
            });
    };

    var searchEntry = function (accession, url) {
        var loader = document.getElementById('loader');
        loader.className = 'modal is-active';

        $.getJSON($SCRIPT_ROOT + url + accession, function (data) {
            loader.className = 'modal';

            window.history.pushState(null, '', data.url);

            if (data.error !== undefined && data.error !== null) {
                document.querySelector('#error .message-header').innerHTML = '<p><strong>'+ data.error.title +'</strong></p>';
                document.querySelector('#error .message-body').innerHTML = data.error.message;
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

    var searchProteinMatches = function (proteinAc) {
        var loader = document.getElementById('loader');
        loader.className = 'modal is-active';

        $.getJSON($SCRIPT_ROOT + '/api/protein/' + proteinAc, function (data) {
            loader.className = 'modal';

            if (data.url !== undefined && data.url !== null)
                window.history.pushState(null, '', data.url);

            if (data.error !== undefined && data.error !== null) {
                document.querySelector('#error .message-header').innerHTML = '<p><strong>'+ data.error.title +'</strong></p>';
                document.querySelector('#error .message-body').innerHTML = data.error.message;
                document.getElementById('error').style.display = 'block';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'none';
                document.getElementById('protein').style.display = 'none';
            } else if (data.type === 'protein') {
                document.getElementById('protein').style.display = 'block';
                updateProteinMatchesSection(data.protein);
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
                document.querySelector('#error .message-header').innerHTML = '<p><strong>'+ data.error.title +'</strong></p>';
                document.querySelector('#error .message-body').innerHTML = data.error.message;
                document.getElementById('error').style.display = 'block';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'none';
                document.getElementById('protein').style.display = 'none';
            } else if (data.type === 'entry') {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'block';
                document.getElementById('entries').style.display = 'none';
                document.getElementById('protein').style.display = 'none';
                updateEntrySection(data.entry);
            } else if (data.type === 'entries') {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'block';
                document.getElementById('protein').style.display = 'none';

                document.querySelector('#entries .title').innerHTML = 'Search results';
                document.querySelector('#entries .subtitle').innerHTML = data.entries.length + ' InterPro entries matching <strong>' + text + '</strong>';

                updateEntriesSection(data.entries);
            } else if (data.type === 'protein') {
                document.getElementById('error').style.display = 'none';
                document.getElementById('entry').style.display = 'none';
                document.getElementById('entries').style.display = 'none';
                document.getElementById('protein').style.display = 'block';
                updateProteinMatchesSection(data.protein);
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
    else if (proteinAc !== null)
        searchProteinMatches(proteinAc);
    else if (search !== null)
        searchText(search);
});