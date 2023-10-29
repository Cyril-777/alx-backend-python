#!/usr/bin/env python3
"""Unittests for client module"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """TestGithubOrgClient class"""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"})
    ])
    @patch('client.get_json')
    def test_org(self, org, expected, mock_get_json):
        """Test that GithubOrgClient.org returns the correct value"""
        mock_get_json.return_value = expected
        client = GithubOrgClient(org)
        self.assertEqual(client.org(), expected)
        link = f'https://api.github.com/orgs/{org}'
        mock_get_json.assert_called_once_with(link)

    def test_public_repos_url(self):
        """Test that the result of _public_repos_url is the expected one"""
        cli = GithubOrgClient('google')
        with patch.object(cli, 'org', new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {'repos_url': 'abc'}
            self.assertEqual(cli._public_repos_url, 'abc')

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test that the list of repos is what
        you expect from the chosen payload."""
        repos = [
            {'name': 'repo1'},
            {'name': 'repo2'}
        ]
        mock_get_json.return_value = repos

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_url:
            mock_url.return_value = 'xyz'

            client = GithubOrgClient('google')
            self.assertEqual(client.public_repos(), ['repo1', 'repo2'])
            mock_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test that GithubOrgClient.has_license returns"""
        client = GithubOrgClient('org')
        self.assertEqual(client.has_license(repo, license_key), expected)


@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """TestIntegrationGithubOrgClient class"""

    @classmethod
    def setUpClass(cls):
        """Set up class"""
        clsbuildside_eff = cls.build_side_effect()
        cls.get_patcher = patch('requests.get', side_effect=clsbuildside_eff)
        cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Tear down class"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that GithubOrgClient.public_repos
        returns the correct list of repos"""
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test that GithubOrgClient.public_repos"""
        client = GithubOrgClient('google')
        self.assertEqual(client.public_repos('apache-2.0'), self.apache2_repos)

    @classmethod
    def build_side_effect(cls):
        """Build side effect"""
        org = cls.org_payload  # org_payload
        r = cls.repos_payload  # repos_payload
        return {
            f'https://api.github.com/orgs/{cls.org_payload["login"]}': org,
            f'https://api.github.com/orgs/{cls.org_payload["login"]}/repos': r
        }
