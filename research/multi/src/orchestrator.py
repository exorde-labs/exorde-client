import asyncio
from aiohttp import web, ClientSession
from dataclasses import dataclass, asdict
from typing import Union
import json

async def get_github_tags_sorted(repo:str): # {owner}/{repo_id}
    async def fetch_json(url:str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()

    tags_url = f"https://api.github.com/repos/{repo}/tags"
    
    tags = await fetch_json(tags_url)
    
    # Parse versions and sort them, / ! \ ignoring any non-semver tags / ! \
    valid_tags = [tag for tag in tags if not version.parse(tag["name"]).is_prerelease]
    sorted_tags = sorted(
        valid_tags,
        key=lambda tag: version.parse(tag["name"]),
        reverse=True
    )

    # Construct the result dictionary with the latest version
    result = {
        "module_name": repo_name,
        "versions": {tag["name"] for tag in sorted_tags},
        "latest": sorted_tags[0]["name"] if sorted_tags else None
    }
    return result


@dataclass
class SpottingIntentParameters:
    pass

@dataclass
class ScraperIntentParameters:
    module: str
    version: str
    keyword: str
    extra_parameters: dict # regular buisness related parameters

@dataclass
class Intent:
    host: str # including port
    params: Union[SpottingIntentParameters, ScraperIntentParameters] 

def scraping_resolver(node) -> Intent:
    return Intent(
        host='{}:{}'.format(node['host'], node['port']),
        params=ScraperIntentParameters(
            module="exorde-labs/rss007d0675444aa13fc",
            version="0.0.3",
            keyword="BITCOIN",
            extra_parameters={

            }
        )
    )


def spotting_resolver(node) -> Intent:
    return Intent(
        host='{}:{}'.format(node['host'], node['port']),
        params=SpottingIntentParameters() # does nothing for spotting, maybe pass worker addr
    )

RESOLVERS = {
    'src.scraper': scraping_resolver,
    'src.spotting': spotting_resolver
}

def think(modules) -> list[Intent]:
    """
    Low Level Note:

    Analog to the brain but instead of generating keywords in generate a list
    of nodes that should be at a specific state, difference here is that:

        - The result now includes the spotting module as the orchestrator should
        theoreticly specify the behavior of every node
        (this would allow us to change the behavior of a node if we are balancing)
    
        - The keyword configuration now also includes the version of the scraping
        module to use.

    note: 

        - The overall thinking behind this architecture is to assume an instable
        software which may interup at anytime (due to pip installs & exit) ; 

        - it also provides us a way to assume the status of the system and have
        enoug data available in order to change the behavior or even topology of
        the system.

        (eg data / failure rate of module/version for behavior)
        (   and capacity evaluation based on spotting threshold )
        (   so for this we would need a way to evaluate nodes capacity )

    For example we will be able in the future to switch from a 4-scrappers 1 
    spotter to 3 scrapper 2 spotters if the spotter is getting overwhelmed.

    ===========================================================================


    Buisness Related Goals:
        - each module should know:
            - what module with which version it sould use
            - what keyword it should scrap with
            - and have it's specific parameters

    """
    result: list[Intent] = []
    def resolve(node: dict) -> Intent:
        return RESOLVERS[node['module']](node)

    for node in app['topology']['modules']:
        if node['module'] == 'src.orchestrator':
            continue
        result.append(resolve(node))
    return result

async def orchestrate(app):
    """
    goal:
        - make sure that scrapers run correct parameters
            - keyword
            - domain_parameters
    """
    while True:
        await asyncio.sleep(1) # to let the servers set up
        print('')
        print('-----------------------')
        print('')
        # create an intent map
        intent = think(app['topology']['modules'])
        # inform the nodes 
        for intent in intent:
            print('\t{}'.format(intent))
            # collect their current status
            try:
                async with ClientSession() as session:
                    async with session.post(
                        'http://{}/status'.format(intent.host), json=json.dumps(asdict(intent))
                    ) as response:
                        response = await response.json()
                        print('\t\t ->{}'.format(response))
            except:
                # if the user add a new client to a running configuration
                # the node would not be available
                # this also helps the orchestrator stay alive if a node dies
                pass
            print('')

        # reflection & introspection

        await asyncio.sleep(app['check_interval'] - 1)

async def start_background_tasks(app):
    app['orchestrate'] = app.loop.create_task(orchestrate(app))

async def cleanup_background_tasks(app):
    app['orchestrate'].cancel()
    await app['orchestrate']

app = web.Application()
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)

app['check_interval'] = 10  # check every 10 seconds
