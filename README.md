# Preferred ranking qualifiers report
Wikidata bot to generate a report page that lists dubious use of the "reason for preferred rank" qualifier.

This report was requested in (Topic:Xlejncl858woc4vg)[https://www.wikidata.org/wiki/Topic:Xlejncl858woc4vg].

## Technical requirements
The bot is currently scheduled to run daily on [Toolforge](https://wikitech.wikimedia.org/wiki/Portal:Toolforge) from within the `msynbot` tool account. It depends on the [shared pywikibot files](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Pywikibot#Using_the_shared_Pywikibot_files_(recommended_setup)) and is running in a Kubernetes environment using Python 3.9.2.
