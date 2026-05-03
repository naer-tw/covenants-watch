# 兩公約 (ICCPR + ICESCR) 施行總檢討平台

> Launch: 2026-04-29 | Methodology: 兒少權 PLAYBOOK Wave 1-92
> Host: 國教行動聯盟 (AABE) 青年部 / 政策倡議室
> Deploy: `policy.aabe.org.tw/two-covenants/`

## Purpose
Document 兩公約's 16 years in Taiwan (2009-2026): official documents, COs, NAP progress, intl. comparisons, **objective evidence of instrumentalization by specific parties / movement groups**. Universal HR must not become shield for any single agenda (LGBTQ+ movement, party tools).

## Red lines (non-negotiable)
1. **Support 兩公約 original spirit** — universal HR (life, liberty, thought/belief, equality, health, education, labor, culture)
2. **Oppose instrumentalization** — distorting 兩公約 as legal grounding for **single issues (esp. LGBTQ+ movement / same-sex marriage / gender identity agenda)**; treaty text + General Comments do not require this
3. **Oppose party-ization** — **specific parties (unnamed; evidence-led)** selectively cite COs to legitimize policy while evading more critical HR problems (child suicide, indigenous rights, labor, religious freedom, free-speech)
4. **Objective evidence first** — article# + source + timestamp; **no emotional language**
5. **Respect religious + conscience freedom** — ICCPR §18 weighed equally with §26; latter must not subsume former
6. **No attacks on individuals / SO persons** — criticize **policy operations of movement groups + agencies**, not personal character

## Dual-axis framework
- **Axis 1 (past unfulfilled)**: COs (1st 2013 Manfred Nowak / 2nd 2017 / 3rd 2022 / 4th 2025), NAP Phase 1 (2022-24) + Phase 2 (2025-28), NHRC monitoring
- **Axis 2 (issues unraised; instrumentalization evidence)**: COs selectively cited, GC vs Taiwan gap, non-progress (child suicide, public health, free-speech, religious freedom, labor, judicial independence, indigenous), party / movement instrumentalization

## Output: 5 versions
Pro / Media (800-1200 字) / Legislative / **Advocacy** (churches, parent groups, partner NGOs) / Social
> No kids version (issues too abstract); replaced with Advocacy.

## Absolute red lines
❌ Name individuals (unless court-ruled) ❌ Emotional/attack language (邪惡/可恥/變態) ❌ Fabricated citations ❌ Unauthorized PII ❌ Interviews without `governance/transcript_citation_sop.md` ❌ Emoji in public HTML (use SVG) ❌ Force push / amend pushed ❌ System brew/pip (use `.venv/bin/pip`) ❌ Notion / Super.so (Markdown SSOT)

## Verify before commit (mandatory — run, don't eyeball)
```bash
bash scripts/self_qa.sh        # must pass; red → fix and re-run
grep -l "本平台立場聲明" <article>.md   # stance disclosure: must appear at start AND end
```
Do **not** report "should be OK" without `self_qa.sh` green.

## Stance disclosure (verbatim Chinese — required at start + end of every article)
```
## 本平台立場聲明
本平台**支持兩公約原始精神**，反對任何政黨或單一議程運動將其工具化。
本文所有指控均附官方出處，對事不對人。
若您發現引用錯誤，請循 `_public/feedback.html` 通報，72 小時內訂正。
```

## Refs
docs/PLATFORM_PLAYBOOK.md · docs/SESSION_HANDOVER.md · data/policy_issues/_PI_PLANNING.md · governance/
