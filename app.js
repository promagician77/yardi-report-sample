(function () {
  'use strict';
  var $ = function (s) { return document.querySelector(s); };
  var money = function (v) { return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
  var cell = function (v) { return v ? v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '–'; };
  var esc = function (s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  document.querySelector('nav').addEventListener('click', function (e) {
    var b = e.target.closest('[role=tab]'); if (!b) return;
    document.querySelectorAll('[role=tab]').forEach(function (t) { t.setAttribute('aria-selected', String(t === b)); });
    document.querySelectorAll('.panel').forEach(function (p) { p.hidden = p.id !== b.dataset.tab; });
    window.scrollTo(0, 0);
  });

  fetch('report_data.json').then(function (r) { return r.json(); }).then(function (d) {
    var asof = new Date(d.as_of + 'T00:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    $('#f-db').textContent = '8 properties · 442 units';
    $('#f-asof').textContent = asof;
    $('#f-ar').textContent = money(d.naive.total);
    $('#r-asof').textContent = asof;

    $('#n-props').textContent = d.naive.properties + ' of 3 allowed';
    $('#n-rows').textContent = d.naive.rows;
    $('#n-ar').textContent = money(d.naive.total);
    $('#s-props').textContent = d.jsmith.properties + ' of 3 allowed';
    $('#s-rows').textContent = d.jsmith.rows;
    $('#s-ar').textContent = money(d.jsmith.total);
    $('#s-list').textContent = d.entitled.join('  ·  ');
    $('#m-props').textContent = d.mchen.properties + ' properties';
    $('#m-rows').textContent = d.mchen.rows;
    $('#m-ar').textContent = money(d.mchen.total);
    $('#l-rows').textContent = d.leak.rows;
    $('#l-amt').textContent = money(d.leak.amount);
    $('#l-list').textContent = d.leak.properties.join('  ·  ');

    // group the secured rows by property, the way SSRS would
    var body = $('#ledger tbody'), html = '', grand = [0, 0, 0, 0, 0], cur = null, sub = null;
    var flush = function () {
      if (!cur) return;
      html += '<tr class="sub"><td class="l" colspan="2">Total &mdash; ' + esc(cur) + '</td>' +
        sub.map(function (v) { return '<td>' + cell(v) + '</td>'; }).join('') + '</tr>';
    };
    d.report_rows.forEach(function (r) {
      if (r.sName !== cur) {
        flush(); cur = r.sName; sub = [0, 0, 0, 0, 0];
        html += '<tr class="grp"><td colspan="7">' + esc(r.sCode) + ' &nbsp;&mdash;&nbsp; ' + esc(r.sName) + '</td></tr>';
      }
      var v = [r.b0, r.b31, r.b61, r.b91, r.total];
      v.forEach(function (x, i) { sub[i] += x; grand[i] += x; });
      html += '<tr class="d"><td class="l">' + esc(r.tenant) + '</td><td class="l u">' + esc(r.sUnitCode) + '</td>' +
        v.map(function (x) { return '<td>' + cell(x) + '</td>'; }).join('') + '</tr>';
    });
    flush();
    html += '<tr class="tot"><td class="l" colspan="2">Grand total &mdash; ' + d.jsmith.properties + ' properties</td>' +
      grand.map(function (x) { return '<td>' + cell(x) + '</td>'; }).join('') + '</tr>';
    body.innerHTML = html;
  }).catch(function () {});

  fetch('files/rpt_aged_delinquency.sql').then(function (r) { return r.text(); }).then(function (t) {
    var h = esc(t)
      .replace(/(\/\*[\s\S]*?\*\/|--[^\n]*)/g, '<span class="cm">$1</span>')
      .replace(/(@[A-Za-z]\w*)/g, '<span class="pm">$1</span>')
      .replace(/\b(CREATE|PROCEDURE|AS|BEGIN|END|SET|NOCOUNT|ON|WITH|SELECT|FROM|JOIN|WHERE|AND|OR|GROUP BY|HAVING|ORDER BY|SUM|CASE|WHEN|THEN|ELSE|IS|NULL|DATEDIFF|BETWEEN|GO|day)\b/g,
        '<span class="kw">$1</span>');
    document.querySelector('#sqlbox').innerHTML = '<code>' + h + '</code>';
  }).catch(function () {});
})();
