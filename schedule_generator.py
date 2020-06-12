import json
import jsonschema
from typing import Dict, Tuple

import datetime


schedule_schema = {
    "type" : "object",
    "properties" : {
        "time" : { "type": "string"},
        "description" : { "type": "string"},
        "title" : { "type": "string"},
        "papers" : {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string" },
                    "url": {"type": "string" },
                    "description": {"type": "string" },
                    "topic": {"type": "string" },
                    "date_proposed": {"type": "string", "format":"date" },
                    "discussion_date": {"type": "string", "format":"date" },
                },
            },
        },
    },
}

def format_paper(paper_dict: Dict[str,str]) -> str:
    markdown = ""
    markdown += f"## {paper_dict['title']}\n"
    markdown += f"### Date: {paper_dict['discussion_date']}\n"
    markdown += f"### Topic: {paper_dict['topic']}\n"
    markdown += f"[Paper link]({paper_dict['url']})\n"
    markdown += f"{paper_dict['description']}\n"
    markdown += f"Date proposed: {paper_dict['date_proposed']}\n"
    markdown += "\n****\n\n"
    return markdown

def get_discussion_date(paper_dict: Dict[str,str]) -> datetime.date:
    return datetime.date.fromisoformat(paper_dict['discussion_date'])

def format_schedule(schedule_path: str,output_path: str) -> str:
    with open(schedule_path) as file:
        schedule = json.load(file)
        jsonschema.validate(instance=schedule, schema=schedule_schema)


    markdown = ""
    markdown += f"# {schedule['title']}\n"
    markdown += f"## Time: {schedule['time']}\n"
    markdown += "\n________\n\n"
    markdown += f"{schedule['description']}\n"
    markdown += "\n****\n"

    current = datetime.date.today()

    new_papers = list()
    old_papers = list()

    for paper in schedule["papers"]:
        paper_date = get_discussion_date(paper)
        if current < paper_date:
            new_papers.append(paper)
        else:
            old_papers.append(paper)

    new_papers.sort(key=get_discussion_date)
    old_papers.sort(key=get_discussion_date)

    for paper in new_papers:
        markdown += format_paper(paper)

    markdown += "\n****************\n"
    markdown += "\n## Old Papers:\n\n"

    for paper in old_papers:
        markdown += format_paper(paper)

    with open(output_path,"w+") as file:
        file.write(markdown)


format_schedule("wednesdaynight.json","README.md")