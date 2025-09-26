INSERT INTO
    common_agents (
        agent_id,
        name,
        enterprise,
        squad
    )
VALUES (
        '11111111-1111-1111-1111-111111111111',
        'Red Data Miner',
        'red',
        'data_miner'
    ) ON CONFLICT (agent_id) DO NOTHING;