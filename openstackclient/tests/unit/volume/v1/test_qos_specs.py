#   Copyright 2015 iWeb Technologies Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import copy
import mock
from mock import call

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.volume.v1 import fakes as volume_fakes
from openstackclient.volume.v1 import qos_specs


class TestQos(volume_fakes.TestVolumev1):

    def setUp(self):
        super(TestQos, self).setUp()

        self.qos_mock = self.app.client_manager.volume.qos_specs
        self.qos_mock.reset_mock()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestQosAssociate(TestQos):

    def setUp(self):
        super(TestQosAssociate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.AssociateQos(self.app, None)

    def test_qos_associate(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            volume_fakes.type_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('volume_type', volume_fakes.type_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.associate.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.type_id
        )
        self.assertIsNone(result)


class TestQosCreate(TestQos):

    columns = (
        'consumer',
        'id',
        'name',
    )
    datalist = (
        volume_fakes.qos_consumer,
        volume_fakes.qos_id,
        volume_fakes.qos_name
    )

    def setUp(self):
        super(TestQosCreate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.CreateQos(self.app, None)

    def test_qos_create_without_properties(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_DEFAULT_CONSUMER),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            {'consumer': volume_fakes.qos_default_consumer}
        )

        self.assertEqual(self.columns, columns)
        datalist = (
            volume_fakes.qos_default_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name
        )
        self.assertEqual(datalist, data)

    def test_qos_create_with_consumer(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
            '--consumer', volume_fakes.qos_consumer
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
            ('consumer', volume_fakes.qos_consumer)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            {'consumer': volume_fakes.qos_consumer}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.datalist, data)

    def test_qos_create_with_properties(self):
        self.qos_mock.create.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_SPECS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_name,
            '--consumer', volume_fakes.qos_consumer,
            '--property', 'foo=bar',
            '--property', 'iops=9001'
        ]
        verifylist = [
            ('name', volume_fakes.qos_name),
            ('consumer', volume_fakes.qos_consumer),
            ('property', volume_fakes.qos_specs)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        specs = volume_fakes.qos_specs.copy()
        specs.update({'consumer': volume_fakes.qos_consumer})
        self.qos_mock.create.assert_called_with(
            volume_fakes.qos_name,
            specs
        )

        columns = self.columns + (
            'specs',
        )
        self.assertEqual(columns, columns)
        datalist = self.datalist + (
            volume_fakes.qos_specs,
        )
        self.assertEqual(datalist, data)


class TestQosDelete(TestQos):

    qos_specs = volume_fakes.FakeQos.create_qoses(count=2)

    def setUp(self):
        super(TestQosDelete, self).setUp()

        self.qos_mock.get = (
            volume_fakes.FakeQos.get_qoses(self.qos_specs))
        # Get the command object to test
        self.cmd = qos_specs.DeleteQos(self.app, None)

    def test_qos_delete_with_id(self):
        arglist = [
            self.qos_specs[0].id
        ]
        verifylist = [
            ('qos_specs', [self.qos_specs[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.delete.assert_called_with(self.qos_specs[0].id, False)
        self.assertIsNone(result)

    def test_qos_delete_with_name(self):
        arglist = [
            self.qos_specs[0].name
        ]
        verifylist = [
            ('qos_specs', [self.qos_specs[0].name])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.delete.assert_called_with(self.qos_specs[0].id, False)
        self.assertIsNone(result)

    def test_qos_delete_with_force(self):
        arglist = [
            '--force',
            self.qos_specs[0].id
        ]
        verifylist = [
            ('force', True),
            ('qos_specs', [self.qos_specs[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.delete.assert_called_with(self.qos_specs[0].id, True)
        self.assertIsNone(result)

    def test_delete_multiple_qoses(self):
        arglist = []
        for q in self.qos_specs:
            arglist.append(q.id)
        verifylist = [
            ('qos_specs', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for q in self.qos_specs:
            calls.append(call(q.id, False))
        self.qos_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_qoses_with_exception(self):
        arglist = [
            self.qos_specs[0].id,
            'unexist_qos',
        ]
        verifylist = [
            ('qos_specs', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.qos_specs[0], exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual(
                    '1 of 2 QoS specifications failed to delete.', str(e))

            find_mock.assert_any_call(self.qos_mock, self.qos_specs[0].id)
            find_mock.assert_any_call(self.qos_mock, 'unexist_qos')

            self.assertEqual(2, find_mock.call_count)
            self.qos_mock.delete.assert_called_once_with(
                self.qos_specs[0].id, False
            )


class TestQosDisassociate(TestQos):

    def setUp(self):
        super(TestQosDisassociate, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.DisassociateQos(self.app, None)

    def test_qos_disassociate_with_volume_type(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--volume-type', volume_fakes.type_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('volume_type', volume_fakes.type_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.disassociate.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.type_id
        )
        self.assertIsNone(result)

    def test_qos_disassociate_with_all_volume_types(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )

        arglist = [
            volume_fakes.qos_id,
            '--all'
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.disassociate_all.assert_called_with(volume_fakes.qos_id)
        self.assertIsNone(result)


class TestQosList(TestQos):

    def setUp(self):
        super(TestQosList, self).setUp()

        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_ASSOCIATIONS),
            loaded=True,
        )
        self.qos_mock.list.return_value = [self.qos_mock.get.return_value]
        self.qos_mock.get_associations.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.qos_association),
            loaded=True,
        )]

        # Get the command object to test
        self.cmd = qos_specs.ListQos(self.app, None)

    def test_qos_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.list.assert_called_with()

        collist = (
            'ID',
            'Name',
            'Consumer',
            'Associations',
            'Specs',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            volume_fakes.qos_id,
            volume_fakes.qos_name,
            volume_fakes.qos_consumer,
            volume_fakes.type_name,
            utils.format_dict(volume_fakes.qos_specs),
        ), )
        self.assertEqual(datalist, tuple(data))


class TestQosSet(TestQos):

    def setUp(self):
        super(TestQosSet, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.SetQos(self.app, None)

    def test_qos_set_with_properties_with_id(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_SPECS),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--property', 'foo=bar',
            '--property', 'iops=9001'
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('property', volume_fakes.qos_specs)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.set_keys.assert_called_with(
            volume_fakes.qos_id,
            volume_fakes.qos_specs
        )
        self.assertIsNone(result)


class TestQosShow(TestQos):

    def setUp(self):
        super(TestQosShow, self).setUp()

        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS_WITH_ASSOCIATIONS),
            loaded=True,
        )
        self.qos_mock.get_associations.return_value = [fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.qos_association),
            loaded=True,
        )]

        # Get the command object to test
        self.cmd = qos_specs.ShowQos(self.app, None)

    def test_qos_show(self):
        arglist = [
            volume_fakes.qos_id
        ]
        verifylist = [
            ('qos_spec', volume_fakes.qos_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.qos_mock.get.assert_called_with(
            volume_fakes.qos_id
        )

        collist = (
            'associations',
            'consumer',
            'id',
            'name',
            'specs'
        )
        self.assertEqual(collist, columns)
        datalist = (
            volume_fakes.type_name,
            volume_fakes.qos_consumer,
            volume_fakes.qos_id,
            volume_fakes.qos_name,
            utils.format_dict(volume_fakes.qos_specs),
        )
        self.assertEqual(datalist, tuple(data))


class TestQosUnset(TestQos):

    def setUp(self):
        super(TestQosUnset, self).setUp()

        # Get the command object to test
        self.cmd = qos_specs.UnsetQos(self.app, None)

    def test_qos_unset_with_properties(self):
        self.qos_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.QOS),
            loaded=True
        )
        arglist = [
            volume_fakes.qos_id,
            '--property', 'iops',
            '--property', 'foo'
        ]

        verifylist = [
            ('qos_spec', volume_fakes.qos_id),
            ('property', ['iops', 'foo'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.qos_mock.unset_keys.assert_called_with(
            volume_fakes.qos_id,
            ['iops', 'foo']
        )
        self.assertIsNone(result)
