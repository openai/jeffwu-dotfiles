import sys
import os
import concurrent.futures

# Placate rcall.global_config, since we don't need OPENAI_USER for this script
os.environ.setdefault("OPENAI_USER", "None")

from rcall.global_config import KUBE_CLUSTERS, CLUSTER_EMOJIS
from rcall.capacity import get_cluster_stats


def main():
    team = "reflection"
    resource_type = "gpu"

    clusters = KUBE_CLUSTERS

    stats = dict()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        for cluster in clusters:
            stats[cluster] = pool.submit(
                get_cluster_stats, team, cluster, resource_type
            )

    free = {
        hl: sum(stats[cluster].result().free[hl] for cluster in clusters)
        for hl in ["high", "low"]
    }
    total_free = free["high"] + free["low"]
    status_str = f"{total_free} Free"
    for cluster in clusters:
        free = stats[cluster].result().free
        emoji = CLUSTER_EMOJIS.get(cluster, ' ')
        status_str += f" {emoji}"
        if free["high"]:
            status_str += f" hi:{free['high']} lo:{free['low']}"
        else:
            status_str += f":{free['low']}"
    print(status_str)
    return


if __name__ == "__main__":
    main()
