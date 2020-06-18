import os
import json
import datetime
import jsonschema
from typing import Dict, Tuple, List, Optional


readme_header = """# AI Village Journal Clubs Schedules

Welcome to the AI Village journal club schedules. The next papers we're discussing are right below this description, 
or checkout the schedules for the individual days for a look further into the future.  


"""

readme_footer = """

# Contributing

If you have a paper you want us to discuss, open a PR with a JSON file with the paper name, link, description, and topic. 
You also have to propose a time and add the date you proposed the paper. There are examples in the folders for the respective days. 
Once the paper has been approved (there will be a little discussion on the PR), we'll merge the PR and regenerate the markdown schedules.
"""

paper_schema = {
    "type": "object",
    "properties": {
        "title": {"type": "string" },
        "url": {"type": "string" },
        "description": {"type": "string" },
        "topic": {"type": "string" },
        "date_proposed": {"type": "string", "format":"date" },
        "discussion_date": {"type": "string", "format":"date" },
    },
}

paper_file_schema = {
  "anyOf": [
    { "type": "array", "items": paper_schema },
    paper_schema,
  ]
}

schedule_schema = {
    "type" : "object",
    "properties" : {
        "time" : { "type": "string"},
        "description" : { "type": "string"},
        "title" : { "type": "string"},
        "papers" : {
            "type": "array",
            "items": paper_schema,
        },
    },
}

def format_paper(paper_dict: Dict[str,str], time: Optional[str]= None, jc_title: Optional[str]= None) -> str:
    markdown = ""
    if jc_title is not None:
        markdown += f"## {jc_title}\n"
    markdown += f"### {paper_dict['title']}\n"
    markdown += f"#### Date: {paper_dict['discussion_date']}\n"
    if time is not None:
        markdown += f"#### Time: {time}\n"
    markdown += f"#### Topic: {paper_dict['topic']}\n"
    markdown += f"[Paper link]({paper_dict['url']})\n"
    markdown += f"{paper_dict['description']}\n"
    markdown += f"Date proposed: {paper_dict['date_proposed']}\n"
    markdown += "\n****\n\n"
    return markdown

def get_discussion_date(paper_dict: Dict[str,str]) -> datetime.date:
    return datetime.date.fromisoformat(paper_dict['discussion_date'])

def open_paper_folder(folder: str) -> List[Dict[str,str]]:
    papers = list()

    files = os.listdir(folder)
    for f in files:
        with open(os.path.join(folder,f)) as file:
            paper_file = json.load(file)
            jsonschema.validate(instance=paper_file, schema=paper_file_schema)
            if type(paper_file) is list:
                papers += paper_file
            else:
                papers.append(paper_file)
    return papers

def sort_paper_discussion_date(
    papers: List[Dict[str,str]],
) -> Tuple[List[Dict[str,str]],List[Dict[str,str]]]:

    current = datetime.date.today()
    new_papers = list()
    old_papers = list()

    for paper in papers:
        paper_date = get_discussion_date(paper)
        if current <= paper_date:
            new_papers.append(paper)
        else:
            old_papers.append(paper)

    new_papers.sort(key=get_discussion_date)
    old_papers.sort(key=get_discussion_date)

    return new_papers,old_papers

def format_schedule(schedule_path: str,output_path: str) -> Optional[str]:
    with open(schedule_path) as file:
        schedule = json.load(file)
        jsonschema.validate(instance=schedule, schema=schedule_schema)

    papers = schedule.get("papers",[])
    papers_dir = schedule.get("papers_dir",None)
    if papers_dir is not None:
        papers += open_paper_folder(papers_dir)
    new_papers,old_papers = sort_paper_discussion_date(papers)

    markdown = ""
    markdown += f"# {schedule['title']}\n"
    markdown += f"## Time: {schedule['time']}\n"
    markdown += "\n________\n\n"
    markdown += f"{schedule['description']}\n"
    markdown += "\n****\n"


    for paper in new_papers:
        markdown += format_paper(paper)

    markdown += "\n****************\n"
    markdown += "\n## Old Papers:\n\n"

    for paper in old_papers:
        markdown += format_paper(paper)

    with open(output_path,"w+") as file:
        file.write(markdown)

    return format_paper(new_papers[0],schedule["time"],schedule["title"])

next_wednesday = format_schedule("wednesdaynight.json","WednesdaySchedule.md")
next_thursday = format_schedule("thursdayafternoon.json","ThursdaySchedule.md")

markdown = readme_header 
if next_wednesday is not None:
    markdown += next_wednesday
if next_thursday is not None:
    markdown += next_thursday
markdown += readme_footer

with open("README.md","w+") as file:
        file.write(markdown)