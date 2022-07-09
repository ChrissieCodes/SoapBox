import json
import logging
from dataclasses import asdict
# import redis

import config
import soapbox.domain.events

logger = logging.getLogger(__name__)

# r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: soapbox.domain.events.Event):
    logging.info("publishing: channel=%s, event=%s", channel, event)
    # r.publish(channel, json.dumps(asdict(event)))




if __name__ == "__main__":
    logger.run()