from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

path = '../logs/sun20201203T0824/events.out.tfevents.1606983882.f0aa0b44b6b3' # Tensorboard ログファイル
event_acc = EventAccumulator(path, size_guidance={'scalars': 0})
event_acc.Reload() # ログファイルのサイズによっては非常に時間がかかる

scalars = {}
for tag in event_acc.Tags()['scalars']:
    events = event_acc.Scalars(tag)
    scalars[tag] = [event.value for event in events]
    
print(scalars)