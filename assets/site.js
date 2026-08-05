/* SHARED PAGE BEHAVIOUR — loaded at the foot of every page.
   The four pages all carry the same header, the same floating contact
   button and the same media rules, so the code that drives them lives here
   once. Each block checks for the markup it needs, because not every page
   has every part: the legal pages, for instance, have no mobile menu.

   Plain script, not a module — these pages have to work opened straight off
   the disk, where the browser refuses modules. */
'use strict';

// ── MOBILE MENU ────────────────────────────────────────────────
// Toggle the panel, swap the hamburger for a close icon, and close again
// once a link is tapped. Homepage and gallery only.
(function () {
    const btn  = document.getElementById('mobileMenuBtn');
    const menu = document.getElementById('mobileMenu');
    if (!btn || !menu) return;

    function setMobileMenu(open) {
        menu.classList.toggle('hidden', !open);
        document.getElementById('menuIconOpen').classList.toggle('hidden', open);
        document.getElementById('menuIconClose').classList.toggle('hidden', !open);
        btn.setAttribute('aria-expanded', open);
    }

    btn.addEventListener('click', () => setMobileMenu(menu.classList.contains('hidden')));
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setMobileMenu(false)));
})();


// ── FLOATING CONTACT BUTTON ────────────────────────────────────
// Opens the phone / WhatsApp / e-mail menu, closes on a click anywhere else.
(function () {
    const toggle = document.getElementById('contactToggle');
    const menu   = document.getElementById('contactMenu');
    if (!toggle || !menu) return;

    toggle.addEventListener('click', () => menu.classList.toggle('hidden'));
    document.addEventListener('click', e => {
        if (!toggle.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.add('hidden');
        }
    });
})();


// ── IMAGE PROTECTION ───────────────────────────────────────────
// Companion to the img/video rules in assets/site.css. Right-click and drag
// are blocked over media only, so text on the page can still be
// right-clicked, selected and copied as normal.
document.addEventListener('contextmenu', e => {
    if (e.target instanceof Element && e.target.closest('img, video')) e.preventDefault();
});
document.addEventListener('dragstart', e => {
    if (e.target instanceof Element && e.target.closest('img, video')) e.preventDefault();
});


// ── LOCAL FILE VIEWING ─────────────────────────────────────────
// The clean URLs (…/gallery/) rely on a web server serving index.html for a
// folder. Opened straight off the disk there is no server to do that, so a
// folder-style link is rewritten to the file itself as it is clicked.
// Harmless on the live site, where this never runs.
if (location.protocol === 'file:') {
    document.addEventListener('click', function (e) {
        var a = e.target && e.target.closest && e.target.closest('a[href]');
        if (!a) return;
        var href = a.getAttribute('href') || '';
        if (/^(?:[a-z][a-z0-9+.-]*:|#)/i.test(href)) return;   // absolute, mailto:, tel:, #anchor
        var parts = href.split('#');
        if (!parts[0].endsWith('/')) return;                   // only folder-style links
        e.preventDefault();
        location.href = parts[0] + 'index.html' + (parts[1] ? '#' + parts[1] : '');
    }, true);
}
