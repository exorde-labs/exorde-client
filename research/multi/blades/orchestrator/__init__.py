"""
The orchestrator is a python process which controls a cluster of exorde modules.

It interface with blade.py which can be any exorde-submodule. It's goal is to
keep the cluster properly configured under exorde's and user's parameters.

1. Version control
    the orchestrator should be able to make a report on the version being used
    by the submodules and what best version should be used. In order to do that
    we need to:
        - Be able to update the scraping module if there is a new version
        - Be able to mark a version as erronous and prevent submodules from
            using it. Effectively rolling back by skipping this version.
        - Report on versions being used by modules
        - Report on all versions
2. Perf control 
    the orchestrator should be able to measure the performance of different
    modules and provide a report on it.
"""

import asyncio
from aiohttp import web, ClientSession
from dataclasses import dataclass, asdict
from typing import Union
import json


"""

So what we do as orchestrator:

    - monitor
        - is craper on correct configuration ?
            - if not , is it running ?
                - stop it
            - configure the scraper
            - start it


The scraper jobs is then to push it's data to a spotting module so we never
receive any data here.


note: start / stop are not process controls but interface controls which are
defined in scraping.py ; we have a .start and .stop endpoint.

This way we can have different scrapers online that do nothing.

"""

async def get_github_tags_sorted(repo:str): # {owner}/{repo_id}
    """This retrieves every tag for a specific module."""
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

"""
Design note on Intents.

The system is designed as a configuration rather than instructions. The goal is
therefor to start, stop, re-configure different modules rather than specificly
follow each instruction and centralize them.

For example for scrapping the interface design is the following :

"""
@dataclass
class ScraperIntentParameters:
    module: str # the scrapping module to use
    version: str # the version the module should use
    keyword: str # the keyword to scrap
    extra_parameters: dict # regular buisness related parameters
    target: str # spotting host to send data to


@dataclass
class SpottingIntentParameters:
    """
    For now there is no specific configuration around the Spotting module
    because it's main_address is configured trough the configuration file
    which is sufficient for static topology.
    """
    pass


@dataclass
class Intent:
    """
    Intents are wrapped to contain a host (they always are meant to an entity)
    """
    host: str # including port
    params: Union[SpottingIntentParameters, ScraperIntentParameters] 

"""
Resolvers are the interface trough which we can express scrappers behavior
changes.

They are tailored for different types of nodes (scraper, spotting, quality)
and allow us to re-configure the node at runtime.

"""

def scraping_resolver(node) -> Intent:
    """
    Using resolvers we can configure nodes parameters such as keywords, timeout
    etc... but most importantly the version of modules. The node will be able
    to re-install a new version in it's venv and restart*.

    *not a container-stop but a process-stop 
    """
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
    """The spotting resolver has no special implementation on static top"""
    return Intent(
        host='{}:{}'.format(node['host'], node['port']),
        params=SpottingIntentParameters() # does nothing for spotting, maybe pass worker addr
    )

RESOLVERS = {
    'src.scraper': scraping_resolver,
    'src.spotting': spotting_resolver
}

def monitor(modules) -> list[Intent]:
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

        - The overall monitoring behind this architecture is to assume an instable
        software which may interup at anytime (due to pip installs & exit) ; 

        - it also provides us a way to assume the status of the system and have
        enough data available in order to change the behavior or even topology
        of the system.

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
        # create an intent map
        intent = monitor(app['topology']['modules'])
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
