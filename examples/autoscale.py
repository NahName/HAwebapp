import requests
import subprocess
import time

PROMETHEUS_URL = 'http://localhost:9090/api/v1/query'
QUERY = 'avg_over_time(container_cpu_usage_seconds_total{container_label_com_docker_swarm_task_name=~"web"}[1m])'
THRESHOLD = 0.5  # пороговое значение CPU загрузки
MIN_REPLICAS = 3
MAX_REPLICAS = 10
CHECK_INTERVAL = 30  # интервал проверки в секундах

def get_average_cpu_usage():
    try:
        response = requests.get(PROMETHEUS_URL, params={'query': QUERY})
        result = response.json()['data']['result']
        if result:
            return float(result[0]['value'][1])
        return 0.0
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        return 0.0

def scale_service(service_name, replicas):
    subprocess.run(['docker-compose', 'up', '--scale', f'{service_name}={replicas}', '-d'])

def main():
    while True:
        cpu_usage = get_average_cpu_usage()
        print(f"Current CPU usage: {cpu_usage}")

        if cpu_usage > THRESHOLD:
            current_replicas = int(subprocess.check_output(['docker-compose', 'ps', '-q', 'web']).decode().strip().count('\n'))
            new_replicas = min(current_replicas + 1, MAX_REPLICAS)
            if new_replicas != current_replicas:
                print(f"Scaling up to {new_replicas} replicas")
                scale_service('web', new_replicas)
        elif cpu_usage < THRESHOLD:
            current_replicas = int(subprocess.check_output(['docker-compose', 'ps', '-q', 'web']).decode().strip().count('\n'))
            new_replicas = max(current_replicas - 1, MIN_REPLICAS)
            if new_replicas != current_replicas:
                print(f"Scaling down to {new_replicas} replicas")
                scale_service('web', new_replicas)
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()

