# Security Policy

Thank you for helping keep BizBuch secure. This document explains how to report security vulnerabilities and how we handle disclosures.

## Reporting a Vulnerability

- Preferred (private): email `Ujjwal.Kar@zohomail.in` with subject `BizBuch Security Report`.
- If you prefer a platform, use GitHub Security Advisories for this repository (private report).

When reporting, please include:
- Affected version(s) or commit hash.
- Clear description of the issue and impact.
- Steps to reproduce, minimal test case, and PoC if available.
- Environment details (Python version, Django version, OS, Docker version if applicable).
- Any relevant logs, stack traces, or screenshots.

If you need to send sensitive exploit details, state that explicitly; we will respond with an encrypted channel if available.

## Response Process & Timeline

- Acknowledgement: within 48 hours of receiving a report.
- Initial triage: within 5 business days.
- Remediation: we aim to provide a fix or mitigation in a timely manner; for most vulnerabilities we target a fix within 90 days. Critical issues may be fixed faster.
- Public disclosure: we will coordinate disclosure with the reporter to allow time for users to upgrade before public announcement.

## Supported Versions

We support the current release and recent stable versions. If you're unsure whether a version is supported, include the version in your report and we will clarify.

| Component | Supported Versions |
|-----------|-------------------|
| Python | 3.10+ |
| Django | 5.2.x |
| PostgreSQL | 15.x |

## CVE and Coordinated Disclosure

If a vulnerability merits a CVE, we will work with the reporter and relevant authorities to request one and publish a coordinated advisory.

## Policy on Public Reports

Please avoid public disclosure of actionable exploit details until a fix is available and users have a reasonable time to upgrade. If a vulnerability is publicly disclosed before a fix, we will treat the issue as high priority.

## Contact

Email: Ujjwal.Kar@zohomail.in

Thank you for helping keep BizBuch safe.
