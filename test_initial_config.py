from main import InitialConfig, Algorithm
import numpy as np

def test_create_confg():
    for i in range(1000):
        q1 = InitialConfig(20)
        config = q1.create_config()
        for segment in range(1, len(config)):
            assert (np.sum(abs(config[segment] - config[segment - 1]))  == 1 or
                        (np.sum(abs(config[segment] - config[segment - 1])) == q1.segment_count-1))



def test_movement():
    for i in range(100):
        q1 = Algorithm(50)
        config = list(q1.movement(1000))[-1]
        for segment in range(1, len(config)):
            if not (np.sum(abs(config[segment] - config[segment - 1]))  == 1 or
                        (np.sum(abs(config[segment] - config[segment - 1])) == q1.segment_count-1)):
                print(config)
                print(config[segment], config[segment - 1], i)
                raise ValueError


#test_create_confg()
test_movement()
