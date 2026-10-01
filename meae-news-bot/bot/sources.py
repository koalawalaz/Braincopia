"""The news sources the bot watches.

Each source is an RSS/Atom feed. Feed URLs change from time to time: run
`python -m bot.check_feeds` on your server to see which ones work, and edit
this list to add, fix or remove sources. `country` is an ISO code used for
the flag in alerts ("INT" for international outlets).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Feed:
    name: str
    url: str
    lang: str  # "en" or "ar"
    country: str


FEEDS: list[Feed] = [
    # ---------------------------------------------------- Pan-Arab / international
    Feed("Al Jazeera English", "https://www.aljazeera.com/xml/rss/all.xml", "en", "QA"),
    Feed("الجزيرة نت", "https://www.aljazeera.net/aljazeerarss/a7c186be-1baa-4bd4-9d80-a84db769f779/73d0e1b4-532f-45ef-b135-bfdff8b8cab9", "ar", "QA"),
    Feed("BBC News Middle East", "https://feeds.bbci.co.uk/news/world/middle_east/rss.xml", "en", "INT"),
    Feed("BBC News Asia", "https://feeds.bbci.co.uk/news/world/asia/rss.xml", "en", "INT"),
    Feed("BBC عربي", "https://feeds.bbci.co.uk/arabic/rss.xml", "ar", "INT"),
    Feed("Al Arabiya English", "https://english.alarabiya.net/feed/rss2/en.xml", "en", "AE"),
    Feed("العربية", "https://www.alarabiya.net/feed/rss2/ar.xml", "ar", "AE"),
    Feed("France 24 Middle East", "https://www.france24.com/en/middle-east/rss", "en", "INT"),
    Feed("France 24 Asia-Pacific", "https://www.france24.com/en/asia-pacific/rss", "en", "INT"),
    Feed("فرانس 24", "https://www.france24.com/ar/rss", "ar", "INT"),
    Feed("DW عربية", "https://rss.dw.com/xml/rss-ar-all", "ar", "INT"),
    Feed("DW Asia", "https://rss.dw.com/xml/rss-en-asia", "en", "INT"),
    Feed("RT Arabic", "https://arabic.rt.com/rss/", "ar", "INT"),
    Feed("CNN Arabic", "https://arabic.cnn.com/api/v1/rss/rss.xml", "ar", "INT"),
    Feed("Sky News Arabia", "https://www.skynewsarabia.com/rss.xml", "ar", "AE"),
    Feed("Independent Arabia", "https://www.independentarabia.com/rss.xml", "ar", "INT"),
    Feed("Middle East Eye", "https://www.middleeasteye.net/rss", "en", "INT"),
    Feed("Al-Monitor", "https://www.al-monitor.com/rss", "en", "INT"),
    Feed("The New Arab", "https://www.newarab.com/rss", "en", "INT"),
    Feed("العربي الجديد", "https://www.alaraby.co.uk/rss", "ar", "INT"),
    Feed("Asharq Al-Awsat English", "https://english.aawsat.com/feed", "en", "SA"),
    Feed("الشرق الأوسط", "https://aawsat.com/feed", "ar", "SA"),
    Feed("The Guardian Middle East", "https://www.theguardian.com/world/middleeast/rss", "en", "INT"),
    Feed("UN News Middle East", "https://news.un.org/feed/subscribe/en/news/region/middle-east/feed/rss.xml", "en", "INT"),
    Feed("UN News Asia-Pacific", "https://news.un.org/feed/subscribe/en/news/region/asia-pacific/feed/rss.xml", "en", "INT"),
    Feed("أخبار الأمم المتحدة", "https://news.un.org/feed/subscribe/ar/news/all/rss.xml", "ar", "INT"),
    # ------------------------------------------------------------------ Gulf
    Feed("Arab News", "https://www.arabnews.com/rss.xml", "en", "SA"),
    Feed("Saudi Gazette", "https://saudigazette.com.sa/rssFeed/74", "en", "SA"),
    Feed("Okaz عكاظ", "https://www.okaz.com.sa/rssFeed/0", "ar", "SA"),
    Feed("Sabq سبق", "https://sabq.org/rss", "ar", "SA"),
    Feed("The National", "https://www.thenationalnews.com/arc/outboundfeeds/rss/?outputType=xml", "en", "AE"),
    Feed("Gulf News", "https://gulfnews.com/feed", "en", "AE"),
    Feed("Khaleej Times", "https://www.khaleejtimes.com/arc/outboundfeeds/rss/?outputType=xml", "en", "AE"),
    Feed("Emarat Al Youm الإمارات اليوم", "https://www.emaratalyoum.com/1.533091?ot=ot.AjaxPageLayout", "ar", "AE"),
    Feed("Gulf Times", "https://www.gulf-times.com/rss", "en", "QA"),
    Feed("The Peninsula", "https://thepeninsulaqatar.com/rss", "en", "QA"),
    Feed("Kuwait Times", "https://kuwaittimes.com/feed/", "en", "KW"),
    Feed("Arab Times Kuwait", "https://www.arabtimesonline.com/feed/", "en", "KW"),
    Feed("Oman Observer", "https://www.omanobserver.om/rssFeed/1", "en", "OM"),
    Feed("Times of Oman", "https://timesofoman.com/rss", "en", "OM"),
    Feed("Gulf Daily News", "https://www.gdnonline.com/rss", "en", "BH"),
    # ----------------------------------------------------------------- Yemen
    Feed("Saba News Agency", "https://www.saba.ye/en/rss.xml", "en", "YE"),
    Feed("Al-Masdar Online المصدر أونلاين", "https://almasdaronline.com/rss", "ar", "YE"),
    Feed("Yemen Monitor يمن مونيتور", "https://www.yemenmonitor.com/rss.xml", "ar", "YE"),
    Feed("South24", "https://south24.net/news/rss.php", "en", "YE"),
    Feed("Aden al-Ghad عدن الغد", "https://adengad.net/rss", "ar", "YE"),
    Feed("Sanaa Center", "https://sanaacenter.org/feed", "en", "YE"),
    Feed("Al-Ayyam الأيام", "https://www.alayyam.info/rss", "ar", "YE"),
    # ------------------------------------------------- Levant, Iraq, Egypt
    Feed("Ahram Online", "https://english.ahram.org.eg/UI/Front/Rss.aspx", "en", "EG"),
    Feed("Egypt Independent", "https://www.egyptindependent.com/feed/", "en", "EG"),
    Feed("Youm7 اليوم السابع", "https://www.youm7.com/rss/SectionRss?SectionID=65", "ar", "EG"),
    Feed("Masrawy مصراوي", "https://www.masrawy.com/rss/feed/25/", "ar", "EG"),
    Feed("Mada Masr", "https://www.madamasr.com/en/feed/", "en", "EG"),
    Feed("Jordan Times", "https://jordantimes.com/rss.xml", "en", "JO"),
    Feed("Roya News", "https://en.royanews.tv/rss", "en", "JO"),
    Feed("Naharnet", "https://www.naharnet.com/stories/en/rss", "en", "LB"),
    Feed("L'Orient Today", "https://today.lorientlejour.com/rss", "en", "LB"),
    Feed("Annahar النهار", "https://www.annahar.com/rss", "ar", "LB"),
    Feed("Enab Baladi English", "https://english.enabbaladi.net/feed/", "en", "SY"),
    Feed("عنب بلدي", "https://www.enabbaladi.net/feed/", "ar", "SY"),
    Feed("SANA English", "https://sana.sy/en/?feed=rss2", "en", "SY"),
    Feed("Rudaw English", "https://www.rudaw.net/english/rss", "en", "IQ"),
    Feed("Kurdistan24", "https://www.kurdistan24.net/en/rss", "en", "IQ"),
    Feed("Shafaq News", "https://shafaq.com/en/rss", "en", "IQ"),
    Feed("شفق نيوز", "https://shafaq.com/ar/rss", "ar", "IQ"),
    Feed("WAFA English", "https://english.wafa.ps/rss.aspx", "en", "PS"),
    Feed("Palestine Chronicle", "https://www.palestinechronicle.com/feed/", "en", "PS"),
    Feed("Times of Israel", "https://www.timesofisrael.com/feed/", "en", "IL"),
    Feed("Jerusalem Post", "https://www.jpost.com/rss/rssfeedsheadlines.aspx", "en", "IL"),
    Feed("Libya Observer", "https://libyaobserver.ly/rss.xml", "en", "LY"),
    Feed("Sudan Tribune", "https://sudantribune.com/feed/", "en", "SD"),
    # ------------------------------------------------------------------ Iran
    Feed("Iran International", "https://www.iranintl.com/en/feed", "en", "IR"),
    Feed("Tehran Times", "https://www.tehrantimes.com/rss", "en", "IR"),
    Feed("IranWire", "https://iranwire.com/en/feed/", "en", "IR"),
    # ---------------------------------------------------------------- Turkey
    Feed("Daily Sabah", "https://www.dailysabah.com/rssFeed/10", "en", "TR"),
    Feed("Hürriyet Daily News", "https://www.hurriyetdailynews.com/rss", "en", "TR"),
    Feed("Anadolu Agency", "https://www.aa.com.tr/en/rss/default?cat=guncel", "en", "TR"),
    Feed("الأناضول", "https://www.aa.com.tr/ar/rss/default?cat=guncel", "ar", "TR"),
    Feed("TRT World", "https://www.trtworld.com/rss", "en", "TR"),
    Feed("TRT عربي", "https://www.trtarabi.com/rss", "ar", "TR"),
    Feed("Turkish Minute", "https://www.turkishminute.com/feed/", "en", "TR"),
    Feed("Bianet English", "https://bianet.org/english/rss", "en", "TR"),
    Feed("Duvar English", "https://www.duvarenglish.com/rss", "en", "TR"),
    # ----------------------------------------------------------- Afghanistan
    Feed("TOLOnews", "https://tolonews.com/rss.xml", "en", "AF"),
    Feed("Khaama Press", "https://www.khaama.com/feed/", "en", "AF"),
    Feed("Amu TV", "https://amu.tv/feed/", "en", "AF"),
    Feed("Ariana News", "https://www.ariananews.af/feed/", "en", "AF"),
    Feed("Pajhwok Afghan News", "https://pajhwok.com/feed/", "en", "AF"),
    Feed("Afghanistan International", "https://www.afintl.com/en/feed", "en", "AF"),
    Feed("Hasht-e Subh", "https://8am.media/eng/feed/", "en", "AF"),
    # ------------------------------------------------------------- Bangladesh
    Feed("The Daily Star", "https://www.thedailystar.net/frontpage/rss.xml", "en", "BD"),
    Feed("Dhaka Tribune", "https://www.dhakatribune.com/feed/", "en", "BD"),
    Feed("The Business Standard", "https://www.tbsnews.net/top-news/rss.xml", "en", "BD"),
    Feed("Prothom Alo English", "https://en.prothomalo.com/feed/", "en", "BD"),
    Feed("New Age", "https://www.newagebd.net/rss/rss.xml", "en", "BD"),
    Feed("The Financial Express BD", "https://thefinancialexpress.com.bd/rss", "en", "BD"),
    Feed("bdnews24", "https://bdnews24.com/?widgetName=rssfeed&widgetId=1150&getXmlFeed=true", "en", "BD"),
    # ---------------------------------------------------------------- Myanmar
    Feed("The Irrawaddy", "https://www.irrawaddy.com/feed", "en", "MM"),
    Feed("Myanmar Now", "https://myanmar-now.org/en/feed/", "en", "MM"),
    Feed("Frontier Myanmar", "https://www.frontiermyanmar.net/en/feed/", "en", "MM"),
    Feed("Mizzima", "https://eng.mizzima.com/feed", "en", "MM"),
    Feed("DVB English", "https://english.dvb.no/feed/", "en", "MM"),
    Feed("Global New Light of Myanmar", "https://www.gnlm.com.mm/feed/", "en", "MM"),
    Feed("Radio Free Asia Myanmar", "https://www.rfa.org/english/news/myanmar/rss2.xml", "en", "MM"),
]


def flag(country: str) -> str:
    """🇸🇦 from "SA"; a globe for international outlets."""
    if len(country) != 2 or not country.isalpha():
        return "🌍"
    return "".join(chr(0x1F1E6 + ord(c) - ord("A")) for c in country.upper())
