import json
import os
import datetime
import csv

# ANSI COLORS
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

sales = []
SALES_FILE = "sales.json"


def save():
    try:
        with open(SALES_FILE, "w") as f:
            json.dump(sales, f, indent=4)
        print(f"{GREEN}Data saved to {SALES_FILE}{RESET}")
    except IOError as e:
        print(f"{RED}Error saving file '{SALES_FILE}': {e}{RESET}")


def load():
    global sales
    if os.path.exists(SALES_FILE):
        try:
            with open(SALES_FILE, "r") as f:
                sales = json.load(f)
            print(f"{GREEN}Data loaded from {SALES_FILE}{RESET}")
        except json.JSONDecodeError:
            print(f"{RED}Error decoding JSON. Starting fresh.{RESET}")
            sales = []
        except IOError as e:
            print(f"{RED}Error loading file: {e}{RESET}")
    else:
        print(f"{YELLOW}{SALES_FILE} not found — starting new list.{RESET}")
        sales = []


def find_item_by_identifier(identifier):
    try:
        target_id = int(identifier)
        for item in sales:
            if item[1] == target_id:
                return item
    except ValueError:
        for item in sales:
            name = item[4][2]
            if name.lower() == identifier.lower():
                return item
    return None


# ---------------------
# EXPORT FUNCTIONS
# ---------------------

def export_csv():
    filename = "sales_export.csv"
    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sold", "ID", "Version", "Date", "Price", "Tags", "Name"])
            for item in sales:
                sold, sid, ver, date, data = item
                price, tags, name = data
                writer.writerow([
                    sold, sid, ver, "/".join(map(str, date)),
                    price, ",".join(tags), name
                ])
        print(f"{GREEN}Exported CSV → {filename}{RESET}")
    except Exception as e:
        print(f"{RED}CSV export failed: {e}{RESET}")


def export_json():
    filename = "sales_export.json"
    try:
        with open(filename, "w") as f:
            json.dump(sales, f, indent=4)
        print(f"{GREEN}Exported JSON → {filename}{RESET}")
    except Exception as e:
        print(f"{RED}JSON export failed: {e}{RESET}")


def export_txt():
    filename = "sales_export.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for item in sales:
                sold, sid, ver, date, data = item
                price, tags, name = data
                f.write(
                    f"ID: {sid} | "
                    f"Status: {'SOLD' if sold else 'PENDING'} | "
                    f"Price: ${price:.2f} | "
                    f"Name: {name} | "
                    f"Tags: {','.join(tags)} | "
                    f"Date: {'/'.join(map(str, date))}\n"
                )
        print(f"{GREEN}Exported TXT → {filename}{RESET}")
    except Exception as e:
        print(f"{RED}TXT export failed: {e}{RESET}")


def export_sd():
    """
    Scorify Document Format (.sd)
    A readable structured format similar to INI or Markdown.
    """
    filename = "sales_export.sd"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write("# SCORIFY DOCUMENT EXPORT\n\n")
            for item in sales:
                sold, sid, ver, date, data = item
                price, tags, name = data
                f.write(f"[Sale {sid}]\n")
                f.write(f"status = {'SOLD' if sold else 'PENDING'}\n")
                f.write(f"price = {price}\n")
                f.write(f"name = {name}\n")
                f.write(f"tags = {','.join(tags)}\n")
                f.write(f"date = {'/'.join(map(str, date))}\n\n")
        print(f"{GREEN}Exported SD → {filename}{RESET}")
    except Exception as e:
        print(f"{RED}SD export failed: {e}{RESET}")


# ---------------------
# MAIN LOOP
# ---------------------

def runcommand():
    print(f"{CYAN}{BOLD}Welcome to Scorify. Type 'help' for commands.{RESET}")
    load()

    while True:
        command = input(f"{BOLD}C:/Scorify/>{RESET} ").strip()
        if not command:
            continue

        data = command.split(" ")
        action = data[0].lower()

        # -------------------
        # CORE COMMANDS
        # -------------------

        if action == "exit":
            save()
            break

        elif action == "help":
            print(f"""
{BOLD}Available commands:{RESET}
  sell <price>            - Add a new sale
  sold <id_or_name>       - Mark as sold
  refund <id_or_name>     - Remove entry
  list                    - Show all entries
  update                  - Reload JSON
  export csv              - Export as CSV
  export txt              - Export as TXT
  export json             - Export as JSON
  export sd               - Export Scorify Document format
  exit                    - Save and quit
""")

        elif action == "sell":
            if len(data) < 2:
                print(f"{RED}Usage: sell <price>{RESET}")
                continue

            try:
                price = float(data[1])
            except ValueError:
                print(f"{RED}Price must be numeric.{RESET}")
                continue

            name = input("> Name: ")
            tags = input("> Tags (comma separated): ")
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]

            now = datetime.datetime.now()
            date_list = [now.year, now.month, now.day]

            max_id = max((item[1] for item in sales), default=0)
            new_id = max_id + 1

            new_entry = [
                False, new_id, 1, date_list, [price, tag_list, name]
            ]
            sales.append(new_entry)

            print(f"{GREEN}Added sale ID {new_id} for '{name}' at ${price:.2f}{RESET}")

        elif action == "sold":
            if len(data) < 2:
                print(f"{RED}Usage: sold <id_or_name>{RESET}")
                continue

            identifier = " ".join(data[1:])
            item = find_item_by_identifier(identifier)

            if not item:
                print(f"{RED}Item not found.{RESET}")
                continue

            if item[0]:
                print(f"{YELLOW}Already marked as sold.{RESET}")
            else:
                item[0] = True
                print(f"{GREEN}Marked as SOLD: {item[4][2]} (ID {item[1]}){RESET}")

        elif action == "refund":
            if len(data) < 2:
                print(f"{RED}Usage: refund <id_or_name>{RESET}")
                continue

            identifier = " ".join(data[1:])
            item = find_item_by_identifier(identifier)

            if not item:
                print(f"{RED}Item not found.{RESET}")
                continue

            sales.remove(item)
            print(f"{GREEN}Refunded + removed ID {item[1]} ('{item[4][2]}'){RESET}")

        elif action == "list":
            print(f"\n{BOLD}Current Sales:{RESET}")

            if not sales:
                print(f"{YELLOW}No sales yet.{RESET}")
            else:
                for item in sales:
                    sold = f"{GREEN}SOLD{RESET}" if item[0] else f"{YELLOW}PENDING{RESET}"
                    price, tags, name = item[4]
                    date_str = "/".join(map(str, item[3]))
                    print(
                        f"{CYAN}ID: {item[1]}{RESET} | "
                        f"{sold} | "
                        f"${price:.2f} | "
                        f"{name} | "
                        f"Tags: {','.join(tags)} | "
                        f"Date: {date_str}"
                    )

            print("-" * 80)

        elif action == "update":
            load()

        # -------------------
        # EXPORT HANDLER
        # -------------------
        elif action == "export":
            if len(data) < 2:
                print(f"{RED}Usage: export <csv|txt|json|sd>{RESET}")
                continue

            fmt = data[1].lower()

            if fmt == "csv":
                export_csv()
            elif fmt == "txt":
                export_txt()
            elif fmt == "json":
                export_json()
            elif fmt == "sd":
                export_sd()
            else:
                print(f"{RED}Unknown export format '{fmt}'{RESET}")

        else:
            print(f"{RED}Unknown command '{action}'. Type 'help'.{RESET}")


if __name__ == "__main__":
    runcommand()
