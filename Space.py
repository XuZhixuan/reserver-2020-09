class Space:
    def __init__(self, identity, name, capacity, available):
        self.identity = identity
        self.name = name
        self.capacity = capacity
        self.available = available
        self.seats = {}
        self.priority = 0

    def update_status(self, session):
        import json
        from login import http_build_query

        url = 'http://rg.lib.xjtu.edu.cn:8086/qseat?' + http_build_query({
            'sp': self.identity
        })

        print('[  OK  ]Requesting: ', url, end='')
        response = session.get(url)
        data = json.loads(response.text)
        print(' ..... done')

        self.available = data['scount'][self.identity][1]

        for key, value in data['seat'].items():
            if key == '' or value == '':
                continue

            self.seats[key] = value == 0
