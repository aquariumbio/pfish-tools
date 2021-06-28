import os
import glob
import re
import json
from copy import copy

def main():
    for filename in glob.iglob('**/test_results.json', recursive=True):
        print(convert_markdown(filename) + "\n")

def convert_markdown(filename):
    newlines = []
    ot_name = operation_type_name(filename)
    newlines.append("# Test {}\n".format(ot_name))

    # Open the file and parse as JSON
    with open(filename, 'r') as f:
        results = json.load(f)

    # Pop out the data that requires special handling
    backtrace = results.pop("backtrace") or []

    # Convert the simple cases
    for key, text in results.items():
        header = key.replace("_", " ").capitalize()
        if isinstance(text, list):
            text = lines_from(text)
        else:
            text = text or ""

        newlines.append(section(header, text))

    newlines.append(hrule())

    # Convert the backtrace
    i = 0
    for event in backtrace:
        header = ""
        text = ""
        operation = event["operation"]
        if operation == "initialize":
            header = "Test started at {}".format(event["time"])
            args = ["{}: {}".format(k, v) for k, v in event["arguments"].items()]
            text = lines_from(args)
        elif operation == "display":
            i += 1
            header = "Step {}\n{}".format(i, hrule())
            text = convert_display(event["content"])
        elif operation == "next":
            continue
        elif operation == "complete":
            continue
        else:
            msg = "## Unrecognized operation: {}\n{}".format(operation, hrule())
            newlines.append(msg)
            continue

        newlines.append(section(header, text))

    with open(filename.replace('.json', '.md'), 'w') as f:
        f.writelines(newlines)

    return "{}:\n{} for {}".format(filename, results['message'], ot_name)

def operation_type_name(filename):
    operation_type_name = "Unknown Operation Type"

    # Get the OperationType name from the definition.json file
    definition_filename = filename.replace('test_results', 'definition')
    if os.path.exists(definition_filename):
        with open(definition_filename, 'r') as f:
            definition = json.load(f)

        operation_type_name = definition["name"]

    return operation_type_name

def lines_from(lst):
    return "\n\n".join(lst)

def section(header, text):
    return "## {}\n{}\n{}".format(header, text, hrule())

def hrule():
    return "\n---\n"

def convert_display(content):
    elements = []
    for element in content:
        element_type, value = element.popitem()
        formatted = format_element(element_type, value)
        elements.append(formatted)

    return lines_from(elements)

def format_element(element_type, value):
    if element_type == "title":
        return format_title(value)
    elif element_type == "note":
        return format_note(value)
    elif element_type == "bullet":
        return format_bullet(value)
    elif element_type == "check":
        return format_check(value)
    elif element_type == "warning":
        return format_warning(value)
    elif element_type == "table":
        return format_table(value)
    elif element_type == "take":
        return format_take(value)
    elif element_type == "separator":
        return hrule()
    else:
        return "{}: {}".format(element_type, value)

def format_title(txt):
    return "### {}".format(txt)

def format_note(txt):
    return "{}".format(txt)

def format_bullet(txt):
    return "  * {}".format(txt)

def format_check(txt):
    return "&#9633; {}".format(txt)

def format_table(tbl):
    formatted = ["<table>"]
    base_style = "border: 1px solid gray; text-align: center"
    for row in tbl:
        newrow = ""
        for cell in row:
            cell_style = copy(base_style)
            if isinstance(cell, dict):
                content = cell.get("content") or "?"
                klass = cell.get("class")
                style = cell.get("style")

                if isinstance(style, dict):
                    cell_style += "; {}".format(style_as_html(style))
                elif klass == "td-filled-slot":
                    cell_style += "; background-color: lightskyblue"
                    cell_style += "; color: black"
            else:
                content = cell

            newrow += "<td style=\"{}\">{}</td>".format(cell_style, content)
        formatted.append("<tr>{}</tr>".format(newrow))

    formatted.append("</table>")
    return "".join(formatted)

def style_as_html(style):
    return "; ".join(["{}: {}".format(k, v) for k, v in style.items()])

def format_take(obj):
    return "Item {} ({}) at {}".format(obj["id"], obj["name"], obj["location"])

def format_warning(txt):
    return "<span style=\"color:orange;\">**{}**</span>".format(txt)

if __name__ == "__main__":
    main()