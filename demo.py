"""Six messages through the pipeline: normalize -> extract -> triage."""
from intake import normalize
from extract import extract
from triage import triage
from fixtures import MESSAGES


def main():
    for raw in MESSAGES:
        msg = normalize(raw)
        ext = extract(msg)
        decision = triage(ext)
        print(f"{msg['id']} ({msg['channel']})  \"{msg['body'][:60]}\"")
        for field, (value, conf) in ext.items():
            if value is not None:
                print(f"    {field}={value} ({conf})")
        print(f"    -> {decision['decision']}  ({decision['why']})\n")


if __name__ == "__main__":
    main()
