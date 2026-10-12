"""Summarize actual hfh.inference events without needing pandas."""
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

def main(path):
    groups = defaultdict(list)
    failures = 0
    for line in Path(path).read_text().splitlines():
        start = line.find('{')
        if start == -1:
            continue
        try:
            event = json.loads(line[start:])
        except json.JSONDecodeError:
            continue
        if event.get('event') == 'gemma_error':
            failures += 1
        if event.get('event') == 'gemma':
            groups[(event['model'], event['contract'])].append(event)
    result = {'failed_calls': failures, 'groups': []}
    for (model, contract), events in sorted(groups.items()):
        values = sorted(event['latency_ms'] for event in events)
        result['groups'].append({'model':model,'contract':contract,'n':len(events),
            'median_ms':statistics.median(values), 'p95_ms_nearest_rank':values[math.ceil(.95*len(values))-1],
            'input_tokens_sum':sum(event.get('input_tokens') or 0 for event in events),
            'output_tokens_sum':sum(event.get('output_tokens') or 0 for event in events),
            'missing_input_token_counts':sum(event.get('input_tokens') is None for event in events),
            'missing_output_token_counts':sum(event.get('output_tokens') is None for event in events)})
    print(json.dumps(result,indent=2))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/summarize_logs.py YOUR_LOG_FILE')
    main(sys.argv[1])
