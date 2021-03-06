from functools import reduce
from flask import session

class NoListeningDataException(Exception):
  def __init__(self, message='You have no listening data to analyze yet!'):
    self.message = message
    super().__init__(self.message)

def convert_to_plot_range(value):
  return (((value - 0) * (1 - -1)) / (1 - 0)) + -1

def get_weight(track_number):
  # First track will start at 0
  x = (track_number - 1) / 10
  y = 1 / 2 ** (x / 0.75)
  return y

def get_top_tracks():
  params = { 'limit': 50, 'offset': 0, 'time_range': 'medium_term' } # Last 6 months
  return session['authorized_client'].get('me/top/tracks', **params).parsed['items']

def get_audio_features(track_ids):
  params = { 'ids': ','.join(track_ids) }
  return session['authorized_client'].get('audio-features', **params).parsed['audio_features']

def get_compass_values(x_axis, y_axis):
  top_track_ids = [ x['id'] for x in get_top_tracks() ]
  if not top_track_ids:
    raise NoListeningDataException

  top_track_audio_features = get_audio_features(top_track_ids)

  total_x_axis = 0
  total_y_axis = 0
  weight_sum = 0

  for track_num, track_features in enumerate(top_track_audio_features):
    weight = get_weight(track_num)
    total_x_axis += (track_features[x_axis] * weight)
    total_y_axis += (track_features[y_axis] * weight)
    weight_sum += weight

  # Weighted average (divide by the sum of all weights)
  mean_x_axis = convert_to_plot_range(total_x_axis / weight_sum)
  mean_y_axis = convert_to_plot_range(total_y_axis / weight_sum)

  return (mean_x_axis, mean_y_axis)
