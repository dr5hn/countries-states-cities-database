/**
 * Slack Notification Helper
 * Sends formatted messages to Slack via webhook.
 * Used by multiple workflows for different notification types.
 */

const https = require('https');
const core = require('@actions/core');

/** Escape text from users (PR titles, logins, file paths) for Slack mrkdwn, where <...> makes links and mentions. */
const esc = (s) => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

/**
 * Send a message to Slack via webhook.
 * @param {string} webhookUrl - Slack incoming webhook URL
 * @param {object} payload - Slack message payload
 * @returns {Promise<boolean>}
 */
async function sendSlackMessage(webhookUrl, payload) {
  return new Promise((resolve) => {
    const data = JSON.stringify(payload);
    const url = new URL(webhookUrl);

    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => (body += chunk));
      res.on('end', () => {
        if (res.statusCode === 200) {
          core.info('Slack notification sent successfully.');
          resolve(true);
        } else {
          core.warning(`Slack notification failed: ${res.statusCode} ${body}`);
          resolve(false);
        }
      });
    });

    req.on('error', (err) => {
      core.warning(`Slack notification error: ${err.message}`);
      resolve(false);
    });

    req.write(data);
    req.end();
  });
}

/**
 * Build a critical PR alert message.
 */
function buildCriticalAlert({ prNumber, prTitle, prUrl, author, reasons }) {
  return {
    attachments: [
      {
        color: '#FF0000',
        blocks: [
          {
            type: 'header',
            text: { type: 'plain_text', text: ':rotating_light: Critical PR Alert', emoji: true },
          },
          {
            type: 'section',
            fields: [
              { type: 'mrkdwn', text: `*PR:* <${prUrl}|#${prNumber}> ${esc(prTitle)}` },
              { type: 'mrkdwn', text: `*Author:* ${esc(author)}` },
            ],
          },
          {
            type: 'section',
            text: {
              type: 'mrkdwn',
              text: `*Reason:*\n${reasons.map((r) => `- ${esc(r)}`).join('\n')}`,
            },
          },
          {
            type: 'actions',
            elements: [
              {
                type: 'button',
                text: { type: 'plain_text', text: 'View PR' },
                url: prUrl,
                style: 'danger',
              },
            ],
          },
        ],
      },
    ],
  };
}

/**
 * Build a PR merged notification.
 */
function buildMergedNotification({ prNumber, prTitle, prUrl, author, summary }) {
  return {
    attachments: [
      {
        color: '#36A64F',
        blocks: [
          {
            type: 'header',
            text: { type: 'plain_text', text: ':white_check_mark: PR Merged', emoji: true },
          },
          {
            type: 'section',
            fields: [
              { type: 'mrkdwn', text: `*PR:* <${prUrl}|#${prNumber}> ${esc(prTitle)}` },
              { type: 'mrkdwn', text: `*Author:* ${esc(author)}` },
            ],
          },
          {
            type: 'section',
            text: { type: 'mrkdwn', text: esc(summary) },
          },
        ],
      },
    ],
  };
}

/**
 * Build a large contribution warning.
 */
function buildLargeContributionWarning({ prNumber, prTitle, prUrl, author, recordCount }) {
  return {
    attachments: [
      {
        color: '#FFA500',
        blocks: [
          {
            type: 'header',
            text: { type: 'plain_text', text: ':warning: Large Contribution', emoji: true },
          },
          {
            type: 'section',
            fields: [
              { type: 'mrkdwn', text: `*PR:* <${prUrl}|#${prNumber}> ${esc(prTitle)}` },
              { type: 'mrkdwn', text: `*Author:* ${esc(author)}` },
              { type: 'mrkdwn', text: `*Records:* ${recordCount}` },
              { type: 'mrkdwn', text: `*Status:* Manual review required` },
            ],
          },
        ],
      },
    ],
  };
}

/**
 * Build weekly digest message.
 */
function buildWeeklyDigest(stats) {
  const date = new Date().toLocaleDateString('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return {
    attachments: [
      {
        color: '#4A90D9',
        blocks: [
          {
            type: 'header',
            text: { type: 'plain_text', text: `:bar_chart: Weekly CSC Digest - ${date}`, emoji: true },
          },
          {
            type: 'section',
            fields: [
              { type: 'mrkdwn', text: `*Open PRs:* ${stats.openPRs} (${stats.newPRs} new)` },
              { type: 'mrkdwn', text: `*Critical:* ${stats.criticalPRs}` },
              { type: 'mrkdwn', text: `*Open Issues:* ${stats.openIssues}` },
              { type: 'mrkdwn', text: `*Merged This Week:* ${stats.mergedPRs}` },
            ],
          },
          ...(stats.topContributors?.length > 0
            ? [
                {
                  type: 'section',
                  text: {
                    type: 'mrkdwn',
                    text:
                      '*Top Contributors:*\n' +
                      stats.topContributors
                        .map((c, i) => `${i + 1}. @${esc(c.login)} (${c.count} PR${c.count > 1 ? 's' : ''})`)
                        .join('\n'),
                  },
                },
              ]
            : []),
        ],
      },
    ],
  };
}

module.exports = {
  sendSlackMessage,
  buildCriticalAlert,
  buildMergedNotification,
  buildLargeContributionWarning,
  buildWeeklyDigest,
};
