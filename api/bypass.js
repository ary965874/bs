import cheerio from 'cheerio';

export default async function handler(req, res) {
  const { url } = req.query;

  if (!url || !url.startsWith('http')) {
    return res.status(400).json({ error: '❌ Invalid or missing `url` parameter' });
  }

  try {
    // Fetch initial page
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
      }
    });

    const html = await response.text();
    const $ = cheerio.load(html);

    const iframeSrc = $('iframe').attr('src');
    if (!iframeSrc) {
      return res.status(404).json({ error: '❌ iframe not found.' });
    }

    const iframeUrl = iframeSrc.startsWith('http') ? iframeSrc : `https://hubcloud.one${iframeSrc}`;

    // Fetch iframe page
    const iframeRes = await fetch(iframeUrl, {
      headers: { Referer: url }
    });

    const iframeHtml = await iframeRes.text();
    const $$ = cheerio.load(iframeHtml);

    let finalLink = $$('a#downloadbtn').attr('href');

    if (!finalLink) {
      $$('a').each((_, el) => {
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
    return res.status(500).json({ error: `❌ Server error: ${err.message}` });
  }
}
