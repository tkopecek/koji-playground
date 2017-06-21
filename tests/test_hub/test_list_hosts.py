import unittest
import mock

import koji
import kojihub

QP = kojihub.QueryProcessor


class TestListHosts(unittest.TestCase):

    def setUp(self):
        self.QueryProcessor = mock.patch('kojihub.QueryProcessor',
                side_effect=self.get_query).start()
        self.queries = []
        self.exports = kojihub.RootExports()

    def tearDown(self):
        mock.patch.stopall()

    def get_query(self, *args, **kwargs):
        query = QP(*args, **kwargs)
        query.execute = mock.MagicMock()
        self.queries.append(query)
        return query

    def test_list_hosts_simple(self):
        self.exports.listHosts()

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, [])

    @mock.patch('kojihub.get_user')
    def test_list_hosts_user_id(self, get_user):
        get_user.return_value = {'id': 99}
        self.exports.listHosts(userID=99)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, ['user_id = %(userID)i'])

    @mock.patch('kojihub.get_channel_id')
    def test_list_hosts_channel_id(self, get_channel_id):
        get_channel_id.return_value = 2
        self.exports.listHosts(channelID=2)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, ['host_channels on host.id = host_channels.host_id'])
        self.assertEqual(query.clauses, ['host_channels.channel_id = %(channelID)i'])

    def test_list_hosts_single_arch(self):
        self.exports.listHosts(arches='x86_64')

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, [r"""(arches ~ E'\\mx86_64\\M')"""])

    def test_list_hosts_multi_arch(self):
        self.exports.listHosts(arches=['x86_64', 's390'])

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, [r"""(arches ~ E'\\mx86_64\\M' OR arches ~ E'\\ms390\\M')"""])

    def test_list_hosts_bad_arch(self):
        with self.assertRaises(koji.GenericError):
            self.exports.listHosts(arches='')

    def test_list_hosts_ready(self):
        self.exports.listHosts(ready=1)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, ['ready is true'])

    def test_list_hosts_nonready(self):
        self.exports.listHosts(ready=0)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, ['ready is false'])

    def test_list_hosts_enabled(self):
        self.exports.listHosts(enabled=1)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, ['enabled is true'])

    def test_list_hosts_disabled(self):
        self.exports.listHosts(enabled=0)

        self.assertEqual(len(self.queries), 1)
        query = self.queries[0]
        self.assertEqual(query.tables, ['host'])
        self.assertEqual(query.joins, [])
        self.assertEqual(query.clauses, ['enabled is false'])
