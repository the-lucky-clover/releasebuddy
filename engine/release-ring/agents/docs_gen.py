"""SCRIBE — the scribe. Generates privacy policy + support page from templates,
customized with your config, as both Markdown and web-ready HTML.
Marks output clearly as templates to review — not legal advice."""
import datetime
import os
import re

from .base import Agent, Result


class DocsAgent(Agent):
    name = "docs"
    purpose = "generate privacy policy + support docs (md + html) from templates"

    def _render(self, text, cfg):
        return re.sub(r"\{\{(\w+)\}\}",
                      lambda m: str(cfg.get(m.group(1), f"[{m.group(1)}]")), text)

    def _md_to_html(self, title, md):
        out = []
        for line in md.split("\n"):
            s = line.strip()
            if s.startswith("### "):
                out.append(f"<h3>{s[4:]}</h3>")
            elif s.startswith("## "):
                out.append(f"<h2>{s[3:]}</h2>")
            elif s.startswith("# "):
                out.append(f"<h1>{s[2:]}</h1>")
            elif s.startswith("> "):
                out.append(f"<blockquote>{s[2:]}</blockquote>")
            elif s.startswith("- "):
                out.append(f"<li>{s[2:]}</li>")
            elif s.startswith("**") and s.endswith("**") and len(s) > 4:
                out.append(f"<p><strong>{s[2:-2]}</strong></p>")
            elif not s:
                out.append("")
            else:
                s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
                s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
                out.append(f"<p>{s}</p>")
        body = "\n".join(out)
        return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>body{{font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:720px;margin:2rem auto;padding:0 1rem;line-height:1.6}}blockquote{{border-left:3px solid #ccc;padding-left:1rem;color:#555}}</style>
</head><body>{body}</body></html>"""

    def run(self, ctx):
        cfg = ctx["cfg"]
        cfg.setdefault("EFFECTIVE_DATE",
                       datetime.date.today().isoformat())
        if not cfg.get("CONTACT_EMAIL"):
            return Result(self.name, False, "set CONTACT_EMAIL in config.env first",
                          ["The docs need a real contact email — stores require one."])
        docs_dir = os.path.join(ctx["repo"], "docs")
        os.makedirs(docs_dir, exist_ok=True)
        made = []
        for name in ("privacy", "support"):
            with open(os.path.join(ctx["repo"], "templates", f"{name}.md")) as f:
                md = self._render(f.read(), cfg)
            with open(os.path.join(docs_dir, f"{name.upper()}.md"), "w") as f:
                f.write(md)
            html = self._md_to_html(f"{cfg.get('APP_NAME', 'App')} — {name.title()}",
                                    md)
            with open(os.path.join(docs_dir, f"{name}.html"), "w") as f:
                f.write(html)
            made.append(f"{name}.html")
        return Result(
            self.name, True,
            "docs generated in docs/ — REVIEW the privacy policy before shipping "
            "(it's a template, not legal advice)",
            made + ["note: advertising section discloses AdMob — required since the "
                    "free version runs ads; the $2.99 Remove Ads IAP is documented "
                    "as the opt-out"])
