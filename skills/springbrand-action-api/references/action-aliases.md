# Action discovery alias map

Use this map when a request names an API service, supplier, platform/product,
model, object, or operation through an abbreviation, alternative spelling, or
non-English name. It converts that wording into one catalogue-facing English
form for `normalized_intent`; it does not choose or authorize an Action.

## Inventory provenance and maintenance

This snapshot was audited on 2026-09-05 with
`action_list_capabilities({ limit: 100 })`. The response contained 52 entries
with `complete: true` and `next_cursor: null`, covering every current Action in
the ten Supplier ID families listed below.

The List response exposes public Action Inventory fields — exact IDs, titles,
summaries, descriptions, recommended prompts, and display order. It does not
expose private aliases or tags. The mappings below are therefore curated from
those public fields and common, unambiguous names; never claim that the service
returned them as alias metadata.

This is a temporary Agent-side discovery aid while the inventory is small. When
the inventory or its public names change, traverse the complete current List
again and update this snapshot. A later server-side discovery improvement should
replace the need for this maintained map.

## Inventory coverage

| Supplier ID family | Entries | Public catalogue families reviewed |
| --- | ---: | --- |
| `supplier.frank.apify` | 9 | Facebook Ad Library; Reddit scraper and monitor; Google Keyword Volume, Maps Reviews, and Trends; Instagram Profile; TikTok Ads and Data |
| `supplier.frank.apollo-io` | 2 | Organization Enrichment; People Search |
| `supplier.frank.elevenlabs` | 1 | Text to Speech |
| `supplier.frank.exa` | 2 | Web Content Extraction; Web Search |
| `supplier.frank.firecrawl` | 3 | Structured Data Extraction; Web Scraping; Web Search and Scrape |
| `supplier.frank.kie-ai-image` | 5 | Seedream 5 Lite image-to-image and text-to-image; Nano Banana 2; GPT Image 2 image-to-image and text-to-image |
| `supplier.frank.kie-ai-video` | 3 | Seedance 2.0 Fast, Mini, and standard video |
| `supplier.frank.people-data-labs` | 2 | Company and Person Enrichment |
| `supplier.frank.serper` | 5 | Google Image, Maps, News, Places, and Shopping Search |
| `supplier.frank.tikhub` | 20 | Instagram (4); Reddit (2); TikTok (4); X (3); Xiaohongshu (4); YouTube (3) |

## Canonicalization rules

- Match case-insensitively after ordinary Unicode normalization. For short
  abbreviations such as `X`, `IG`, `TT`, `YT`, `PDL`, `TTS`, `T2I`, and `I2V`,
  require a whole token and capability-relevant context.
- Prefer the longest, most specific alias when forms overlap. Preserve explicit
  model variants such as `Fast` and `Mini`, and preserve every platform,
  supplier, operation, object, and modality constraint the user actually gave.
- Emit one canonical form in `normalized_intent`. Do not stuff aliases into the
  body and do not fan out multiple Match calls.
- An alias supplies only the concept in its row. A platform alias does not
  invent an operation or object, and a model-family alias does not invent a
  version or input modality.
- Treat the canonicalized concept as a hard compatibility constraint when the
  user stated it explicitly. Include a supplier in `normalized_intent` only
  when the user explicitly requires that supplier.

## Service and supplier aliases

Every current entry uses a `supplier.frank.*` Supplier ID. `Frank` alone is
non-discriminating across the present inventory, so omit it from
`normalized_intent` unless the user explicitly makes it a constraint.

| Canonical form | Curated aliases | Current inventory family |
| --- | --- | --- |
| `Apify` | — | `supplier.frank.apify` |
| `Apollo` | `Apollo.io`, `Apollo IO` | `supplier.frank.apollo-io` |
| `ElevenLabs` | `Eleven Labs`, `11Labs` | `supplier.frank.elevenlabs` |
| `Exa` | `Exa.ai` | `supplier.frank.exa` |
| `Firecrawl` | `Fire Crawl` | `supplier.frank.firecrawl` |
| `Kie.ai` | `Kie AI`, `KIE` | `supplier.frank.kie-ai-image`, `supplier.frank.kie-ai-video` |
| `People Data Labs` | `PDL`, `PeopleDataLabs`, `People DataLabs` | `supplier.frank.people-data-labs` |
| `Serper` | `Serper.dev` | `supplier.frank.serper` |
| `TikHub` | `Tik Hub` | `supplier.frank.tikhub` |

## Platform and product aliases

| Canonical form | Curated aliases | Current inventory scope |
| --- | --- | --- |
| `Facebook Ad Library` | `Facebook Ads Library`, `FB Ad Library`, `Meta Ad Library`, `Meta Ads Library`, `脸书广告库` | `action.apify.scrape_facebook_ad_library` |
| `Reddit` | `红迪` | `action.apify.scrape_reddit__practical-tools-apify`, `action.apify.monitor_reddit_mentions`, `action.tikhub.reddit-*` |
| `Google Keyword Volume` | `Google Search Volume`, `keyword search volume`, `关键词搜索量` | `action.apify.keyword_volume` |
| `Google Maps` | `Google Map`, `GMaps`, `谷歌地图` | `action.apify.scrape_google_maps_reviews`, `action.serper.maps` |
| `Google Trends` | `GTrends`, `谷歌趋势` | `action.apify.scrape_google_trends` |
| `Instagram` | `IG`, `Insta` | `action.apify.scrape_profiles`, `action.tikhub.instagram-*` |
| `TikTok Ads Library` | `TikTok Ads`, `TikTok广告库` | `action.apify.scrape_tiktok_ads_library` |
| `TikTok` | `Tik Tok`, `TT`, `抖音国际版`, `国际版抖音` | `action.apify.tiktok_api`, `action.tikhub.tiktok-*` |
| `Douyin` | `抖音`, `抖音短视频` | `catalogue-summary-only` |
| `X` | `Twitter`, `推特`, `X.com`, `X/Twitter` | `action.tikhub.twitter-*` |
| `Xiaohongshu` | `xhs`, `小红书`, `RedNote`, `Red Note`, `little red book`, `RED` | `action.tikhub.xhs-*` |
| `YouTube` | `YT`, `You Tube`, `油管` | `action.tikhub.youtube-*` |
| `Google Image` | `Google Images`, `谷歌图片` | `action.serper.images` |
| `Google News` | `谷歌新闻` | `action.serper.news` |
| `Google Places` | `Google Place`, `谷歌地点` | `action.serper.places` |
| `Google Shopping` | `谷歌购物` | `action.serper.shopping` |
| `Web` | `website`, `web page`, `网页`, `网站` | `action.exa.*`, `action.firecrawl.*` |

`Douyin` appears in the TikHub catalogue summary, but the audited 52-entry
inventory has no dedicated Douyin Action. Preserve `Douyin` as the platform
constraint and, if complete Match plus List recovery finds no compatible
entry, report no current fit. Never silently rewrite `Douyin` to `TikTok`.
Likewise, treat bare `X` as the social platform only when the surrounding
request refers to posts, profiles, social search, or `X.com`.

## Model and vendor aliases

| Canonical form | Curated aliases | Current inventory scope |
| --- | --- | --- |
| `ByteDance` | `Bytedance`, `字节跳动`, `字节` | `action.kie-ai-image.seedream-*`, `action.kie-ai-video.bytedance-*` |
| `Seedream` | `即梦`, `即梦AI` | `action.kie-ai-image.seedream-5-lite-*` |
| `Seedream 5 Lite` | `Seedream5 Lite` | `action.kie-ai-image.seedream-5-lite-*` |
| `Nano Banana 2` | `NanoBanana2`, `Nano Banana` | `action.kie-ai-image.google-nanobanana2` |
| `OpenAI` | `Open AI` | `action.kie-ai-image.gpt-gpt-image-2-*` |
| `GPT Image 2` | `GPT-Image-2`, `GPT Image2` | `action.kie-ai-image.gpt-gpt-image-2-*` |
| `Seedance 2.0` | `Seedance 2`, `Seedance2` | `action.kie-ai-video.bytedance-seedance-2*` |

`Nano Banana` currently resolves to `Nano Banana 2` because it is the only
Nano Banana family in this inventory snapshot. Re-audit that shorthand as
soon as another version appears. Bare `Seedream` is a family form; `Seedream
5 Lite` is the exact current model. Retain every explicit version, `Fast`, or
`Mini` modifier instead of silently selecting one.

## Object, modality, and operation aliases

| Canonical form | Curated aliases | Current inventory meaning |
| --- | --- | --- |
| `Search` | `find`, `look up`, `lookup`, `query`, `搜索`, `查找`, `检索` | Locate existing catalogue data. |
| `Details` | `detail`, `info`, `information`, `详情`, `详细信息` | Fetch one exact post, note, or video. |
| `User Profile` | `profile`, `account profile`, `user info`, `账号资料`, `用户资料`, `主页` | Fetch a public account profile. |
| `User Posts` | `account posts`, `author posts`, `用户帖子`, `账号内容` | List content published by one user. |
| `Comments` | `comment`, `replies`, `responses`, `评论`, `回复` | Fetch replies on one content item. |
| `Reviews` | `review`, `ratings`, `评价`, `评分` | Fetch Google Maps reviews. |
| `Monitor` | `track`, `watch`, `monitoring`, `监控`, `追踪` | Monitor Reddit brand mentions. |
| `Scrape` | `scraper`, `crawl`, `抓取`, `爬取` | Retrieve public web or social data. |
| `Extract` | `extraction`, `抽取`, `提取` | Extract web content or structured fields. |
| `Enrichment` | `enrich`, `data enrichment`, `补全`, `数据补充` | Enrich a person, company, or organization. |
| `Post` | `posts`, `帖子`, `动态` | A social post; `tweet` and `推文` mean `X Post` only in X/Twitter context. |
| `Note` | `notes`, `笔记` | A Xiaohongshu content item. |
| `Video` | `videos`, `短视频` | A TikTok or YouTube video, or generated video. |
| `Image` | `images`, `picture`, `photo`, `图片`, `图像` | An existing or generated image. |
| `Text to Speech` | `TTS`, `text2speech`, `txt2speech`, `文本转语音`, `语音合成` | ElevenLabs speech generation. |
| `Text to Image` | `T2I`, `text2image`, `txt2img`, `文生图`, `文字生成图片` | Generate an image from text. |
| `Image to Image` | `I2I`, `image2image`, `img2img`, `图生图`, `图片编辑` | Edit or transform an existing image. |
| `Text to Video` | `T2V`, `text2video`, `txt2vid`, `文生视频`, `文字生成视频` | Generate video with text input. |
| `Image to Video` | `I2V`, `image2video`, `img2vid`, `图生视频`, `图片生成视频` | Generate video with image input. |

Operation and modality mappings are compatibility constraints, not synonyms
for one another. `Search` cannot satisfy `Details`; `Comments` cannot satisfy
`User Posts`; `Text to Image` cannot satisfy `Image to Image`; and `Text to
Video` cannot satisfy `Image to Video` when the user explicitly requires the
input modality.
