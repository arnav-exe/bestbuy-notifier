import requests
from dotenv import load_dotenv
import os

load_dotenv()


def post_ntfy(body, ntfy_topic):
    requests.post(
        ntfy_topic,
        data=body,
        headers={
            "Title": "BestBuy Alert",
            "Priority": "default",
            "Tags": "loudspeaker",
            "Icon": "https://corporate.bestbuy.com/wp-content/uploads/thegem-logos/logo_0717ce843a2125d21ef450e7f05f352e_1x.png",
            "Markdown": "yes",
        }
    )


def ntfy_delete(topic: str, sequence_id: str):  # feature still in development
    return requests.delete(f"https://ntfy.sh/{topic}/{sequence_id}")


if __name__ == "__main__":
    noti_body = "Click [this link](https://api.bestbuy.com/click/-/6575404/pdp) to view the product"

    ntfy_topic = os.getenv("NTFY_TOPIC_URL")

    post_ntfy(noti_body, ntfy_topic)
