__main__.py for starting the code and this then calls agent.py for the agentic works and only works to connect to fastapi and make the code accessible to the outside world and models.py is just used for the sake of its running.

agent.py creates all the classes for core modules and then uses langchain.agents to then further send the call to tools.py

tools.py then combines planner, executor and aggregator answers to send the results back again to agent.py and followed to __main__.py

tools.py calling to planner.py , executor.py and aggregator.py and combine with connecting everything...

planner.py gives the tasks part and later send the point to executer.py

executor.py then asks router.py to send the modules their individual works

aggregator.py then combines everything i.e. each code is being concatenation along with betterment via LLMs

-- base_module.py is giving a former well defined defination for all the modules.

Now executor.py is going to call all the modules.

-- Modules
culture_analyzer.py ->

-- Utils
config.py -> empty

database.py -> connects to database and have all functionalities of candidates like entry filling of name, email etc. and interview etc. being saved
gmail.py -> sends offer letters, interview mail etc. mails for the candidates along with the authentification
google_calendar.py -> connecting to calendar, create events, get events, find slots, cancel events etc.
logger.py -> empty
mongodb_database.py -> connects to database and all functionalities of candidates like adding removing etc.