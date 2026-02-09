@patch("time.sleep", return_value=None)
@patch('sleepy.sleep_add', return_value=3)
@patch('sleepy.sleep_multiply', return_value=5)
