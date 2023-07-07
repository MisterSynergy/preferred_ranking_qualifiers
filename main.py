from io import StringIO
from time import strftime

import pandas as pd
import pywikibot as pwb
import requests


WDQS_ENDPOINT = 'https://query.wikidata.org/sparql'
WDQS_USER_AGENT = f'{requests.utils.default_user_agent()} (Wikidata bot by User:MisterSynergy; mailto:mister.synergy@yahoo.com)'

WD = 'http://www.wikidata.org/entity/'
WDS = 'http://www.wikidata.org/entity/statement/'
WIKIBASE = 'http://wikiba.se/ontology#'

DISPLAY_LIMIT = 2500

SITE = pwb.Site('wikidata', 'wikidata')
REPORT_PAGE_TITLE = 'Property talk:P7452/qualifiers to check'


def query_wdqs(query:str) -> str:
    response = requests.post(
        url=WDQS_ENDPOINT,
        data={
            'query' : query
        },
        headers={
            'User-Agent': WDQS_USER_AGENT,
            'Accept' : 'text/csv'
        }
    )

    return response.text


def query_to_dataframe(query, columns):
    df = pd.read_csv(
        StringIO(query_wdqs(query)),
        header=0,
        names=list(columns.keys()),
        dtype=columns
    )

    return df


def query_cases() -> pd.DataFrame:
    columns = {
        'item' : str,
        'property' : str,
        'propertyLabel' : str,
        's' : str,
        'rank' : str,
        'reason' : str,
        'reasonLabel' : str,
    }

    query = """SELECT ?item ?property ?propertyLabel ?s ?rank ?reason ?reasonLabel WITH {
  SELECT ?s ?rank ?reason WHERE {
    ?s pq:P7452 ?reason; wikibase:rank ?rank .
    FILTER(?rank != wikibase:PreferredRank) .
  }
} AS %subquery WHERE {
  INCLUDE %subquery .
  ?item ?p ?s .
  ?property wikibase:claim ?p .
  SERVICE wikibase:label { bd:serviceParam wikibase:language 'en' }
}"""

    df = query_to_dataframe(query, columns)

    df['item'] = df['item'].str.removeprefix(WD)
    df['property'] = df['property'].str.removeprefix(WD)
    df['s'] = df['s'].str.removeprefix(WDS)
    df['s'] = df['s'].str.replace('-', '$', n=1)
    df['rank'] = df['rank'].str.removeprefix(WIKIBASE)
    df['reason'] = df['reason'].str.removeprefix(WD)

    return df


def make_report(df:pd.DataFrame) -> str:
    report = f'List of statements with {{{{Property|P7452}}}} qualifier that do not carry [[Help:Ranking#Preferred rank|preferred rank]]. Cases found: {df.shape[0]}. Last update: <onlyinclude>{strftime("%Y-%m-%d %H:%M (%Z)")}</onlyinclude>\n\n'

    if df.shape[0] > DISPLAY_LIMIT:
        df = df.head(DISPLAY_LIMIT)
        report += f'This report has been truncated to {DISPLAY_LIMIT} cases.\n\n'

    report += """{| class="wikitable sortable"
|-
! item !! property !! rank !! reason
"""
    
    for elem in df.itertuples():
        if not elem.reason.startswith('http://www.wikidata.org/.well-known/genid/'):
            reason_link = f'[[{elem.reason}|{elem.reasonLabel}]]'
        else:
            reason_link = '{{Unknown value}}'

        if elem.item.startswith('Q'):
            item_link = f'{elem.item}#{elem.s}'
        elif elem.item.startswith('P'):
            item_link = f'Property:{elem.item}#{elem.s}'
        elif elem.item.startswith('L'):
            item_link = f'Lexeme:{elem.item}#{elem.s}'

        report += f"""|-
| [[{item_link}|{elem.item}]] || [[Property:{elem.property}|{elem.propertyLabel}]] || {elem.rank} || {reason_link}
"""

    report += """|}"""

    return report


def write_to_wiki(report:str) -> None:
    page = pwb.Page(SITE, REPORT_PAGE_TITLE)
    page.text = report
    page.save(summary='upd', minor=False)


def main():
    df = query_cases()
    report = make_report(df)
    write_to_wiki(report)


if __name__=='__main__':
    main()
