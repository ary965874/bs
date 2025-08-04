import cheerio from 'cheerio';
import fetch from 'node-fetch';

export default async function handler(req, res) {
  const { url } = req.query;

  if (!url || !url.startsWith('http')) {
    return res.status(400).json({ error: '❌ Invalid or missing `url` parameter' });
  }

  try {
    // Step 1: Fetch main HubCloud page
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
      }
    });

    if (!response.ok) {
      return res.status(500).json({ error: `❌ Failed to fetch main page. Status ${response.status}` });
    }

    const html = await response.text();
    const $ = cheerio.load(html);

    // Step 2: Extract iframe
    const iframeSrc = $('iframe').attr('src');
    if (!iframeSrc) {
      return res.status(404).json({ error: '❌ iframe not found on page.' });
    }

    const iframeUrl = iframeSrc.startsWith('http') ? iframeSrc : `https://hubcloud.one${iframeSrc}`;

    // Step 3: Fetch iframe content
    const iframeRes = await fetch(iframeUrl, {
      headers: { Referer: url }
    });

    if (!iframeRes.ok) {
      return res.status(500).json({ error: `❌ Failed to fetch iframe. Status ${iframeRes.status}` });
    }

    const iframeHtml = await iframeRes.text();
    const $$ = cheerio.load(iframeHtml);

    // Step 4: Find download button or link
    let finalLink = $$('a#downloadbtn').attr('href');

    if (!finalLink) {
      // Fallback: Try other <a> tags with 'download' text
      $$('a').each((i, el) => {
        const text = $$(el).text().toLowerCase();
        const href = $$(el).attr('href');
        if (text.includes('download') && href?.startsWith('http') && !finalLink) {
          finalLink = href;
        }
      });
    }

    if (!finalLink) {
      return res.status(404).json({ error: '❌ Download link not found.' });
    }

    return res.status(200).json({
      success: true,
      url: finalLink
    });

  } catch (err) {
    return res.status(500).json({ error: `❌ Error: ${err.message}` });
  }
}
