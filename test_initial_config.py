from main import InitialConfig, Algorithm

def test_create_confg():
    for i in range(100):
        q1 = InitialConfig(20)
        config = q1.create_config()
        for position in range(len(config) - 1):
            assert abs(config[position][0] - config[position + 1][0] +
                       config[position + 1][1] - config[position][1]) \
                   in (1, len(config) - 1, len(config) + 1)

def test_movement():
    for i in range(100):
        q1 = Algorithm(100)
        config = q1.movement(1000)
        for position in range(len(config) - 1):
            assert abs(config[position][0] - config[position + 1][0] +
                       config[position + 1][1] - config[position][1]) \
                   in (1, len(config) - 1, len(config) + 1)
    print(config)

test_create_confg()
test_movement()