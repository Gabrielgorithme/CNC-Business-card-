# Notes for Claude

## Git
- Commit and push after each completed change, without waiting to be asked. Push to the session's working branch; never force-push and never push to `main` unless Gabriel asks.

## The site (docs/)
- The URL is engraved in the card's QR code and can never change: https://gabrielgorithme.github.io/CNC-Business-card-/ (GitHub Pages from `main` /docs). Use relative paths.
- Pages are generated: edit `site/build.py`, then run `python3 site/build.py`. Don't hand-edit `docs/index.html`, `docs/fr/index.html` or `docs/404.html`.
- English and French versions are kept in step.
- Write the copy the way Gabriel talks: first person, everyday words people actually use ("Tupperware", never "a plastic food box"), contractions, his own humour. No sanitised assistant tone, no report-speak: it's his personal site and that reads as AI-written.
- Client brands from Ambiance Lumière are never named (copy, alt text, file names): "a luxury fashion house". Notre-Dame de Paris may be named.
- Gabriel's phone number stays off the site and out of the repository.

## CV and achievements
- The master list of Gabriel's achievements, facts and numbers is his private Claude Doc "Gabriel's CV achievements": https://claude.ai/artifact/JhrF8QGyXovgVKySrH9MJQ (open it with the docs tools). Use it when redoing the CV or the site copy, and keep it updated when he shares new facts.
