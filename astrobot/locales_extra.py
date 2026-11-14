"""Human-readable, bundled translations; no network needed for the interface."""

BASE = {
    "zh": """
welcome=欢迎来到 Falino ✨ 今天想探索什么？先看看运势，也可以保存生日，让我们每天陪伴你。
daily=今日运势
weekly=本周运势
monthly=本月运势
yearly=年度运势
birth=出生日期
profile=我的资料
language=语言
tarot=每日塔罗
schedule=接收时间
subscribe=开启/关闭每日推送
back=主菜单
choose=请选择你的星座 ✨
saved=已保存 ✅
error=服务暂时开小差了，请稍后再试 🌿
birth_prompt=请按年-月-日发送日期，例如 1995-04-12。
calendar=请选择出生日期使用的历法
gregorian=公历
jalali=波斯历
invalid=格式好像不对，请按示例重试，或发送 /cancel。
need_birth=先保存生日或选择星座吧 ✨
clock_prompt=请发送时间和时区，例如：08:30 Asia/Shanghai
join=先加入这些频道，再点击「检查加入状态」。
check=检查加入状态
join_failed=尚未确认加入，请加入全部必需频道后重试。
no_year=管理员还没有发布这个星座的中文年度运势。
annual_note=年度运势 · 由机器人编辑发布
source_date=来源日期
original=翻译暂不可用，下面显示英文原文。
fun=仅供娱乐
on=已开启 🌞
off=已关闭 🌙
delete=删除我的数据
confirm_delete=确定删除个人资料并停止每日推送吗？
confirm=确认删除
deleted=你的资料已删除。随时发送 /start 再来玩 ✨
about=运势按星座选取，同一星座会收到相同来源内容。出生年份会保存，但该接口不提供按出生年份生成的专属每日运势。
mood=心情日记
mood_prompt=今天心情如何？发送 1–10 的数字。/moods 可查看最近七次记录。
compat=星座趣味配对
compat_note=根据传统星座元素进行的趣味比较，不是对关系的预测。
ref=邀请朋友
moon=月相
moon_note=根据平均朔望周期估算月相，并非精密天文历表。
new=新月
waxing=盈月
full=满月
waning=亏月
stale=提醒：来源日期与今天不同。
natal=出生时行星位置
natal_prompt=请先保存生日，再发送出生时间与出生地时区：14:30 Asia/Shanghai。此功能显示行星位置，不含上升星座、宫位或完整星盘解读。
natal_note=地心热带黄道行星位置；不含上升星座与宫位
""",
    "hi": """
welcome=Falino में स्वागत है ✨ आज क्या जानना चाहेंगे? अपना जन्मदिन सहेजें और रोज़ हमारे साथ जुड़ें।
daily=आज का राशिफल
weekly=इस सप्ताह
monthly=इस महीने
yearly=इस वर्ष
birth=जन्म तिथि
profile=मेरी प्रोफ़ाइल
language=भाषा
tarot=आज का टैरो
schedule=संदेश का समय
subscribe=दैनिक संदेश चालू/बंद
back=मुख्य मेन्यू
choose=अपनी राशि चुनें ✨
saved=सहेज लिया ✅
error=सेवा अभी उपलब्ध नहीं है। थोड़ी देर में फिर कोशिश करें 🌿
birth_prompt=तिथि वर्ष-महीना-दिन में भेजें, जैसे 1995-04-12।
calendar=जन्म तिथि का कैलेंडर चुनें
gregorian=ग्रेगोरियन
jalali=सौर हिजरी
invalid=प्रारूप सही नहीं है। उदाहरण के अनुसार भेजें या /cancel करें।
need_birth=पहले जन्म तिथि सहेजें या राशि चुनें ✨
clock_prompt=समय और समय क्षेत्र भेजें, जैसे: 08:30 Asia/Kolkata
join=पहले इन चैनलों से जुड़ें, फिर सदस्यता जाँचें।
check=सदस्यता जाँचें
join_failed=सदस्यता की पुष्टि नहीं हुई। सभी आवश्यक चैनलों से जुड़ें।
no_year=इस राशि और भाषा का वार्षिक राशिफल अभी प्रकाशित नहीं हुआ है।
annual_note=वार्षिक राशिफल · बॉट संपादक द्वारा प्रकाशित
source_date=स्रोत की तिथि
original=अनुवाद उपलब्ध नहीं है; नीचे मूल अंग्रेज़ी पाठ है।
fun=केवल मनोरंजन के लिए
on=चालू 🌞
off=बंद 🌙
delete=मेरा डेटा हटाएँ
confirm_delete=प्रोफ़ाइल हटाएँ और दैनिक संदेश रोकें?
confirm=हटाने की पुष्टि
deleted=आपका डेटा हटा दिया गया है। फिर मिलने के लिए /start भेजें ✨
about=राशिफल राशि के आधार पर चुना जाता है। एक राशि वाले लोगों को समान स्रोत पाठ मिलता है। जन्म वर्ष सहेजा जाता है, लेकिन यह API जन्म वर्ष पर आधारित व्यक्तिगत दैनिक भविष्यवाणी नहीं देता।
mood=मन का हाल
mood_prompt=आज कैसा महसूस कर रहे हैं? 1 से 10 भेजें। पिछले सात रिकॉर्ड: /moods।
compat=राशियों की मज़ेदार तुलना
compat_note=पारंपरिक राशि तत्वों पर आधारित मनोरंजक तुलना; संबंधों की भविष्यवाणी नहीं।
ref=दोस्तों को बुलाएँ
moon=चंद्रमा की अवस्था
moon_note=औसत चंद्र चक्र से निकला अनुमान; सटीक खगोलीय गणना नहीं।
new=अमावस्या
waxing=बढ़ता चंद्रमा
full=पूर्णिमा
waning=घटता चंद्रमा
stale=ध्यान दें: स्रोत की तिथि आज से अलग है।
natal=जन्म के समय ग्रह
natal_prompt=पहले जन्म तिथि सहेजें। फिर जन्म का समय और स्थान का समय क्षेत्र भेजें: 14:30 Asia/Kolkata। लग्न, भाव और पूरी कुंडली की व्याख्या शामिल नहीं है।
natal_note=भूकेंद्रीय उष्णकटिबंधीय ग्रह स्थितियाँ; लग्न और भाव शामिल नहीं
""",
    "ru": """
welcome=Добро пожаловать в Falino ✨ Заглянем в твой день? Сохрани дату рождения — будем встречаться каждый день.
daily=На сегодня
weekly=На неделю
monthly=На месяц
yearly=На год
birth=Дата рождения
profile=Мой профиль
language=Язык
tarot=Карта дня
schedule=Время доставки
subscribe=Ежедневная рассылка вкл/выкл
back=Главное меню
choose=Выбери свой знак ✨
saved=Сохранено ✅
error=Сервис временно недоступен. Попробуй немного позже 🌿
birth_prompt=Отправь дату в формате ГГГГ-ММ-ДД, например 1995-04-12.
calendar=Выбери календарь даты рождения
gregorian=Григорианский
jalali=Солнечная хиджра
invalid=Формат не подошёл. Следуй примеру или отправь /cancel.
need_birth=Сначала сохрани дату рождения или выбери знак ✨
clock_prompt=Отправь время и часовой пояс: 08:30 Europe/Moscow
join=Подпишись на эти каналы, затем проверь подписку.
check=Проверить подписку
join_failed=Подписка не подтверждена. Подпишись на все обязательные каналы.
no_year=Годовой прогноз для этого знака и языка ещё не опубликован.
annual_note=Годовой прогноз · опубликован редактором бота
source_date=Дата источника
original=Перевод недоступен; ниже оригинал на английском.
fun=Для развлечения
on=Включено 🌞
off=Выключено 🌙
delete=Удалить мои данные
confirm_delete=Удалить профиль и остановить ежедневную рассылку?
confirm=Подтвердить удаление
deleted=Данные удалены. Возвращайся через /start ✨
about=Прогноз выбирается по знаку зодиака. Люди одного знака получают одинаковый исходный текст. Год рождения сохраняется, но API не даёт персональный ежедневный прогноз по году рождения.
mood=Дневник настроения
mood_prompt=Как ты сегодня? Отправь число от 1 до 10. Последние семь записей: /moods.
compat=Совместимость знаков
compat_note=Развлекательное сравнение по традиционным стихиям, а не прогноз отношений.
ref=Пригласить друзей
moon=Фаза Луны
moon_note=Приблизительная фаза по среднему лунному циклу, не точная эфемерида.
new=Новолуние
waxing=Растущая Луна
full=Полнолуние
waning=Убывающая Луна
stale=Внимание: дата источника отличается от сегодняшней.
natal=Планеты при рождении
natal_prompt=Сначала сохрани дату рождения. Затем отправь время и часовой пояс места рождения: 14:30 Europe/Moscow. Без асцендента, домов и полной интерпретации карты.
natal_note=Геоцентрические тропические положения планет; без асцендента и домов
""",
    "he": """
welcome=ברוכים הבאים ל־Falino ✨ רוצים להציץ ביום שלכם? שמרו תאריך לידה וניפגש כאן בכל יום.
daily=היום
weekly=השבוע
monthly=החודש
yearly=השנה
birth=תאריך לידה
profile=הפרופיל שלי
language=שפה
tarot=קלף יומי
schedule=שעת קבלה
subscribe=הפעלה/כיבוי שליחה יומית
back=תפריט ראשי
choose=בחרו את המזל שלכם ✨
saved=נשמר ✅
error=השירות אינו זמין כרגע. נסו שוב מאוחר יותר 🌿
birth_prompt=שלחו תאריך בפורמט שנה-חודש-יום, למשל 1995-04-12.
calendar=בחרו לוח שנה לתאריך הלידה
gregorian=גרגוריאני
jalali=היג׳רי שמשי
invalid=הפורמט אינו תקין. שלחו לפי הדוגמה או /cancel.
need_birth=שמרו קודם תאריך לידה או בחרו מזל ✨
clock_prompt=שלחו שעה ואזור זמן, למשל: 08:30 Asia/Jerusalem
join=הצטרפו לערוצים הבאים ואז בדקו חברות.
check=בדיקת חברות
join_failed=החברות לא אושרה. הצטרפו לכל הערוצים הנדרשים.
no_year=עדיין לא פורסמה תחזית שנתית למזל ולשפה האלה.
annual_note=תחזית שנתית · פורסמה על ידי עורך הבוט
source_date=תאריך המקור
original=תרגום אינו זמין; מוצג הטקסט המקורי באנגלית.
fun=לבידור בלבד
on=פעיל 🌞
off=כבוי 🌙
delete=מחיקת הנתונים שלי
confirm_delete=למחוק את הפרופיל ולהפסיק שליחה יומית?
confirm=אישור מחיקה
deleted=הנתונים נמחקו. אפשר לחזור עם /start ✨
about=התחזית נבחרת לפי מזל. אנשים מאותו מזל מקבלים אותו טקסט מקור. שנת הלידה נשמרת, אך הממשק אינו מספק תחזית יומית אישית לפי שנת לידה.
mood=יומן מצב רוח
mood_prompt=איך אתם היום? שלחו מספר מ־1 עד 10. שבע הרשומות האחרונות: /moods.
compat=התאמה בין מזלות
compat_note=השוואה משעשעת לפי היסודות המסורתיים, ולא חיזוי של מערכות יחסים.
ref=הזמנת חברים
moon=מופע הירח
moon_note=הערכה לפי מחזור ירח ממוצע; לא חישוב אסטרונומי מדויק.
new=מולד הירח
waxing=ירח מתמלא
full=ירח מלא
waning=ירח מתמעט
stale=שימו לב: תאריך המקור שונה מהיום.
natal=מיקומי כוכבי הלכת בלידה
natal_prompt=שמרו קודם תאריך לידה. שלחו שעת לידה ואזור זמן של מקום הלידה: 14:30 Asia/Jerusalem. ללא אופק, בתים או פירוש מפה מלא.
natal_note=מיקומים גאוצנטריים בגלגל טרופי; ללא אופק ובתים
""",
    "es": """
welcome=¡Bienvenido a Falino! ✨ ¿Vemos qué trae tu día? Guarda tu cumpleaños y nos encontramos cada mañana.
daily=Hoy
weekly=Esta semana
monthly=Este mes
yearly=Este año
birth=Fecha de nacimiento
profile=Mi perfil
language=Idioma
tarot=Carta del día
schedule=Hora de entrega
subscribe=Activar/desactivar envío diario
back=Menú principal
choose=Elige tu signo ✨
saved=Guardado ✅
error=El servicio no está disponible ahora. Prueba un poco más tarde 🌿
birth_prompt=Envía la fecha como AAAA-MM-DD; por ejemplo, 1995-04-12.
calendar=Elige el calendario de nacimiento
gregorian=Gregoriano
jalali=Hijri solar
invalid=El formato no es correcto. Sigue el ejemplo o envía /cancel.
need_birth=Primero guarda tu fecha de nacimiento o elige un signo ✨
clock_prompt=Envía la hora y zona horaria, por ejemplo: 08:30 Europe/Madrid
join=Únete a estos canales y después comprueba tu membresía.
check=Comprobar membresía
join_failed=No se confirmó la membresía. Únete a todos los canales obligatorios.
no_year=Todavía no hay una lectura anual para este signo e idioma.
annual_note=Lectura anual · publicada por el editor del bot
source_date=Fecha de la fuente
original=La traducción no está disponible; se muestra el original en inglés.
fun=Solo para entretenimiento
on=Activado 🌞
off=Desactivado 🌙
delete=Eliminar mis datos
confirm_delete=¿Eliminar tu perfil y detener el envío diario?
confirm=Confirmar eliminación
deleted=Tus datos se eliminaron. Vuelve cuando quieras con /start ✨
about=Las lecturas se eligen por signo. Las personas del mismo signo reciben el mismo texto de origen. Se guarda el año de nacimiento, pero la API no ofrece predicciones diarias individuales por año de nacimiento.
mood=Diario de ánimo
mood_prompt=¿Cómo estás hoy? Envía un número del 1 al 10. Últimos siete registros: /moods.
compat=Compatibilidad de signos
compat_note=Comparación lúdica de elementos tradicionales; no predice relaciones.
ref=Invitar amigos
moon=Fase lunar
moon_note=Fase aproximada basada en un ciclo lunar medio; no es una efeméride precisa.
new=Luna nueva
waxing=Creciente
full=Luna llena
waning=Menguante
stale=Aviso: la fecha de la fuente es distinta de hoy.
natal=Planetas al nacer
natal_prompt=Guarda primero tu fecha de nacimiento. Envía la hora y la zona horaria del lugar de nacimiento: 14:30 Europe/Madrid. Sin ascendente, casas ni interpretación completa de la carta.
natal_note=Posiciones planetarias geocéntricas tropicales; sin ascendente ni casas
""",
    "fr": """
welcome=Bienvenue chez Falino ✨ On découvre ta journée ? Enregistre ta date de naissance et retrouvons-nous chaque matin.
daily=Aujourd’hui
weekly=Cette semaine
monthly=Ce mois-ci
yearly=Cette année
birth=Date de naissance
profile=Mon profil
language=Langue
tarot=Carte du jour
schedule=Heure de réception
subscribe=Activer/désactiver l’envoi quotidien
back=Menu principal
choose=Choisis ton signe ✨
saved=Enregistré ✅
error=Le service fait une petite pause. Réessaie un peu plus tard 🌿
birth_prompt=Envoie la date au format AAAA-MM-JJ, par exemple 1995-04-12.
calendar=Choisis le calendrier de naissance
gregorian=Grégorien
jalali=Hégirien solaire
invalid=Le format ne convient pas. Suis l’exemple ou envoie /cancel.
need_birth=Enregistre d’abord ta date de naissance ou choisis ton signe ✨
clock_prompt=Envoie l’heure et le fuseau horaire : 08:30 Europe/Paris
join=Rejoins ces chaînes puis vérifie ton abonnement.
check=Vérifier l’abonnement
join_failed=L’abonnement n’est pas confirmé. Rejoins toutes les chaînes requises.
no_year=Aucune lecture annuelle n’a encore été publiée pour ce signe et cette langue.
annual_note=Lecture annuelle · publiée par l’éditeur du bot
source_date=Date de la source
original=Traduction indisponible ; voici le texte original en anglais.
fun=Pour le divertissement
on=Activé 🌞
off=Désactivé 🌙
delete=Supprimer mes données
confirm_delete=Supprimer ton profil et arrêter l’envoi quotidien ?
confirm=Confirmer la suppression
deleted=Tes données ont été supprimées. Reviens quand tu veux avec /start ✨
about=Les lectures sont choisies selon le signe. Les personnes du même signe reçoivent le même texte source. L’année de naissance est enregistrée, mais l’API ne fournit pas de prédiction quotidienne individuelle selon cette année.
mood=Carnet d’humeur
mood_prompt=Comment vas-tu aujourd’hui ? Envoie un nombre de 1 à 10. Les sept dernières entrées : /moods.
compat=Compatibilité des signes
compat_note=Comparaison ludique des éléments traditionnels ; ce n’est pas une prédiction de relation.
ref=Inviter des amis
moon=Phase lunaire
moon_note=Phase approximative basée sur un cycle lunaire moyen ; pas une éphéméride précise.
new=Nouvelle Lune
waxing=Lune croissante
full=Pleine Lune
waning=Lune décroissante
stale=Attention : la date de la source est différente d’aujourd’hui.
natal=Planètes à la naissance
natal_prompt=Enregistre d’abord ta date de naissance. Envoie l’heure et le fuseau du lieu de naissance : 14:30 Europe/Paris. Sans ascendant, maisons ni interprétation complète du thème.
natal_note=Positions planétaires géocentriques tropicales ; sans ascendant ni maisons
""",
}

# Same key order for each column below. Templates retain their named fields.
EXTRA_KEYS = """support support_prompt support_sent support_reply tickets ticket_closed no_items history favorites favorite unfavorite feedback liked disliked streak quests reward claim claimed points days collection spread spread_note past present future partners partner_prompt name_prompt limited privacy privacy_text faq faq_text birthday_text welcome_privacy daily_task weekly_task reward_note""".split()
EXTRA = {
    "en": """💬 Contact our team|Tell us what’s on your mind, in one message (up to 1800 characters). You can attach a photo, voice note or document. /cancel to leave.|Your message is safely in our inbox 💌 Ticket #{id}. You’ll get our reply right here.|💌 A reply from the Falino team · #{id}|My support tickets|This ticket is closed. Open a new one with /support.|Nothing here yet 🌱|My reading history|My favorites|⭐ Save|Remove favorite|Was this reading helpful?|Thanks for sharing your thoughts 💛|Thanks — we’ll keep improving 🌿|My daily streak|My little quests|My stars|Claim today’s stars|You’ve already claimed this reward ✨|Stars|Days|My tarot collection|Three-card tarot|A playful past, present and future spread; each meaning comes from the source cards, not a prediction of events.|Past|Present|Future|Saved partners|Send a nickname and sign: Alex | aries|What should we call you? Send a name up to 40 characters.|Let’s take a little pause. Please try again soon 🌿|Privacy & my data|We store the Telegram profile fields available to the bot, the birth details you enter, readings and support messages. Administrators can see them; when configured, profile and reading activity are sent to the private staff log. We cannot see your phone number or private chats. /delete_me removes local personal records and requests deletion of tracked staff copies; Telegram limits or old backups may prevent full removal there. Birth-time calculations send those details to the astrology API. Translation sends public source readings only.|Quick help|Daily readings come from your zodiac sign. Save your birth date, choose a delivery time, then turn on daily messages. Use /support to talk to us, /history to revisit readings, /rewards for your stars, and /stop to stop notifications.|🎂 Happy birthday, {name}! A little extra sparkle for your day — we’re glad you’re here 💛|Your profile and reading activity are visible to the staff for support and moderation. Details: /privacy.|Daily reading + mood check|Three days of visits this week|Stars are free in-bot points, with no cash value or payment requirement.""",
    "fa": """💬 ارتباط با تیم فالینو|هرچی توی دلت هست برامون بگو 💌 پیامت رو یک‌جا بفرست؛ تا ۱۸۰۰ حرف. عکس، ویس یا فایل هم می‌تونی ضمیمه کنی. انصراف: /cancel|پیامت رسید دستمون 💌 تیکت #{id} ثبت شد؛ جوابمون همین‌جا برات میاد.|💌 پاسخ تیم فالینو · تیکت #{id}|پیام‌های پشتیبانی من|این تیکت بسته شده؛ برای پیام تازه /support رو بزن 🌿|اینجا هنوز خبری نیست؛ کم‌کم پرش می‌کنیم 🌱|دفتر فال‌های من|فال‌های محبوبم|⭐ نگهش دار|از محبوب‌ها بردار|این فال به دلت نشست؟|مرسی که نظرت رو گفتی 💛|مرسی؛ کمک می‌کنی بهترش کنیم 🌿|روزهای همراهی من|چالش‌های کوچولوی من|ستاره‌های من|ستاره امروز رو بگیر|ستاره این بخش رو قبلاً گرفتی ✨|ستاره|روز|کلکسیون تاروت من|تاروت سه‌کارتی|یک چیدمان تفننی گذشته، حال و آینده؛ معنی‌ها از کارت‌های منبع هستند و پیش‌بینی رویداد واقعی نیستند.|گذشته|حال|آینده|دوست‌های ذخیره‌شده|اسم مستعار و برج رو بفرست؛ نمونه: سارا / aries|دوست داری چی صدات کنیم؟ یک اسم تا ۴۰ حرف بفرست 💛|یه نفس کوچولو بگیریم 🌿 کمی بعد دوباره امتحان کن.|حریم خصوصی و داده‌ها|مشخصات تلگرامی در دسترس ربات، اطلاعات تولدی که خودت ثبت می‌کنی، فال‌ها و پیام‌های پشتیبانی ذخیره می‌شوند و برای مدیر قابل مشاهده‌اند. اگر گروه لاگ تنظیم شود، مشخصات و فعالیت فال در گروه خصوصی تیم هم ثبت می‌شود. ربات شماره تلفن یا گفت‌وگوهای خصوصی تو را نمی‌بیند. /delete_me داده‌های شخصی محلی را حذف می‌کند و حذف نسخه‌های ثبت‌شده گروه را درخواست می‌دهد؛ محدودیت تلگرام یا بکاپ قدیمی می‌تواند مانع حذف آن نسخه‌ها شود. محاسبه سیارات، تاریخ و ساعت تولد را به API نجومی می‌فرستد؛ ترجمه فقط متن عمومی فال را می‌فرستد.|راهنمای کوچولو|از تاریخ تولد شروع کن، ساعت دریافت رو بچین و ارسال روزانه رو روشن کن 🌞 برای حرف‌زدن با ما /support، دفتر فال‌ها /history، ستاره‌ها /rewards و توقف پیام‌ها /stop رو بزن.|🎂 {name} جان، تولدت مبارک! خوشحالیم یک سال دیگه از قصه‌ات رو کنار هم می‌بینیم 💛|مشخصات و فعالیت فالت برای پشتیبانی و مدیریت قابل مشاهده است؛ توضیحات: /privacy.|فال روزانه + ثبت حال امروز|سه روز سرزدن در این هفته|ستاره‌ها امتیاز رایگان داخل ربات‌اند؛ ارزش پولی یا نیاز به پرداخت ندارند.""",
    "ar": """💬 تواصل مع فريق فالينو|احكِ لنا ما يشغلك في رسالة واحدة، حتى 1800 حرف. يمكنك إرفاق صورة أو رسالة صوتية أو ملف. للإلغاء /cancel.|وصلتنا رسالتك 💌 التذكرة #{id}. سنرد عليك هنا.|💌 رد فريق فالينو · #{id}|تذاكري|أُغلقت هذه التذكرة. لرسالة جديدة استخدم /support.|لا شيء هنا بعد 🌱|سجل قراءاتي|قراءاتي المفضلة|⭐ احفظها|إزالة من المفضلة|هل أعجبتك القراءة؟|شكراً لمشاركة رأيك 💛|شكراً؛ تساعدنا على التحسين 🌿|أيام متابعتي|تحدياتي الصغيرة|نجومي|احصل على نجوم اليوم|حصلت على هذه المكافأة مسبقاً ✨|نجمة|يوم|مجموعة التاروت|تاروت ثلاث بطاقات|قراءة ترفيهية للماضي والحاضر والمستقبل؛ المعاني من البطاقات وليست تنبؤاً بأحداث حقيقية.|الماضي|الحاضر|المستقبل|الأصدقاء المحفوظون|أرسل اسماً مستعاراً والبرج، مثال: سارة / aries|بماذا نناديك؟ أرسل اسماً حتى 40 حرفاً 💛|لنأخذ استراحة قصيرة. حاول لاحقاً 🌿|الخصوصية وبياناتي|نحفظ بيانات تلغرام المتاحة للبوت، وتفاصيل الميلاد التي تدخلها والقراءات ورسائل الدعم. يراها المدير، وقد تُرسل إلى سجل الفريق الخاص عند تفعيله. لا نرى رقم هاتفك أو محادثاتك الخاصة. /delete_me يحذف البيانات الشخصية المحلية ويطلب حذف نسخ السجل؛ قد تمنع قيود تلغرام أو النسخ الاحتياطية القديمة حذفها بالكامل. تُرسل تفاصيل الميلاد إلى API لحساب الكواكب، والترجمة تستخدم نص القراءة العام فقط.|مساعدة سريعة|سجّل ميلادك، اختر وقت الرسائل وفعّل الإرسال اليومي. للدعم /support، للسجل /history، للنجوم /rewards، ولإيقاف الرسائل /stop.|🎂 عيد ميلاد سعيد يا {name}! سعداء بوجودك معنا 💛|بياناتك ونشاط القراءات متاحان للفريق للدعم والإدارة. التفاصيل: /privacy.|قراءة يومية + تسجيل المزاج|زيارة البوت ثلاثة أيام هذا الأسبوع|النجوم نقاط مجانية داخل البوت، دون قيمة نقدية أو دفع.""",
    "zh": """💬 联系 Falino 团队|想说什么都可以告诉我们 💌 请一次发送，不超过 1800 字。可附照片、语音或文件。退出：/cancel。|收到你的消息啦 💌 工单 #{id}，回复会发到这里。|💌 Falino 团队回复 · #{id}|我的工单|此工单已关闭。请用 /support 发起新工单。|这里还空着呢 🌱|我的运势记录|我的收藏|⭐ 收藏|取消收藏|这次解读对你有帮助吗？|谢谢你的反馈 💛|谢谢，我们会继续改进 🌿|连续陪伴天数|我的小任务|我的星星|领取今日星星|这项奖励已经领取过啦 ✨|星星|天|塔罗收藏册|三张塔罗|以过去、现在和未来为主题的娱乐牌阵；解释来自卡片，不代表事件预测。|过去|现在|未来|已保存的朋友|发送昵称和星座，例如：小明 / aries|希望我们怎么称呼你？发送不超过 40 字的昵称 💛|休息一下吧，请稍后再试 🌿|隐私与数据|我们保存机器人可获取的 Telegram 资料、你填写的生日信息、阅读记录和客服消息。管理员可查看；配置后也会发送到私有团队日志。我们无法查看你的手机号或私人聊天。/delete_me 删除本地个人记录并请求删除已跟踪的团队日志副本；Telegram 限制或旧备份可能阻止彻底删除。出生时行星计算会向星象 API 发送生日和时间，翻译仅发送公共运势文本。|快速帮助|保存生日，设置时间并开启每日推送。客服：/support，记录：/history，星星：/rewards，停止推送：/stop。|🎂 {name}，生日快乐！很开心有你陪伴 💛|团队可查看你的资料和运势活动以提供支持。详情：/privacy。|每日运势 + 心情记录|本周来访三天|星星是免费的机器人内积分，没有现金价值，也无需付费。""",
    "hi": """💬 Falino टीम से बात करें|मन की बात एक संदेश में भेजें, अधिकतम 1800 अक्षर। फोटो, वॉइस या फ़ाइल जोड़ सकते हैं। बाहर जाने के लिए /cancel।|आपका संदेश मिल गया 💌 टिकट #{id}। जवाब यहीं आएगा।|💌 Falino टीम का जवाब · #{id}|मेरे सहायता टिकट|यह टिकट बंद है। नया संदेश भेजने के लिए /support।|अभी यहाँ कुछ नहीं है 🌱|मेरे राशिफल का इतिहास|मेरे पसंदीदा|⭐ सहेजें|पसंदीदा से हटाएँ|क्या यह अच्छा लगा?|राय देने के लिए धन्यवाद 💛|धन्यवाद, हम इसे और बेहतर बनाएँगे 🌿|लगातार आने के दिन|मेरे छोटे लक्ष्य|मेरे सितारे|आज के सितारे लें|यह इनाम पहले ही मिल चुका है ✨|सितारे|दिन|मेरा टैरो संग्रह|तीन कार्ड टैरो|अतीत, वर्तमान और भविष्य का मनोरंजक फैलाव; अर्थ कार्ड से हैं, वास्तविक घटनाओं की भविष्यवाणी नहीं।|अतीत|वर्तमान|भविष्य|सहेजे गए साथी|नाम और राशि भेजें, जैसे: आरव / aries|आपको क्या कहकर बुलाएँ? 40 अक्षरों तक नाम भेजें 💛|थोड़ा विराम लें। कुछ देर बाद फिर कोशिश करें 🌿|गोपनीयता और मेरा डेटा|हम बॉट को उपलब्ध Telegram प्रोफ़ाइल, आपके भरे जन्म विवरण, पढ़ाइयाँ और सहायता संदेश सहेजते हैं। प्रशासक इन्हें देख सकते हैं; सेट होने पर निजी टीम लॉग में भी भेजे जाते हैं। हम फ़ोन नंबर या निजी चैट नहीं देख सकते। /delete_me स्थानीय व्यक्तिगत रिकॉर्ड हटाता है और ट्रैक किए लॉग हटाने का अनुरोध करता है; Telegram की सीमाएँ या पुराने बैकअप पूरी तरह हटने से रोक सकते हैं। ग्रह गणना के लिए जन्म तिथि और समय API को भेजे जाते हैं; अनुवाद में केवल सार्वजनिक पाठ जाता है।|छोटी सी मदद|जन्म तिथि सहेजें, समय चुनें और दैनिक संदेश चालू करें। सहायता /support, इतिहास /history, सितारे /rewards, संदेश रोकें /stop।|🎂 {name}, जन्मदिन मुबारक! आपके साथ होने की खुशी है 💛|सहायता और प्रबंधन के लिए टीम आपकी प्रोफ़ाइल और गतिविधि देख सकती है। विवरण: /privacy।|दैनिक राशिफल + मन का हाल|इस सप्ताह तीन दिन आएँ|सितारे मुफ़्त इन-बॉट अंक हैं; इनका नकद मूल्य नहीं और भुगतान आवश्यक नहीं।""",
    "ru": """💬 Написать команде|Расскажи, что тебя волнует, одним сообщением до 1800 символов. Можно прикрепить фото, голосовое или файл. Выход: /cancel.|Сообщение у нас 💌 Обращение #{id}. Ответ придёт сюда.|💌 Ответ команды Falino · #{id}|Мои обращения|Обращение закрыто. Для нового сообщения: /support.|Здесь пока пусто 🌱|История прогнозов|Избранное|⭐ Сохранить|Убрать из избранного|Прогноз понравился?|Спасибо за твой отзыв 💛|Спасибо, будем улучшать 🌿|Моя серия дней|Мои маленькие задания|Мои звёзды|Забрать звёзды дня|Эта награда уже получена ✨|Звёзды|Дни|Моя коллекция Таро|Три карты Таро|Развлекательный расклад о прошлом, настоящем и будущем; значения взяты из карт и не предсказывают реальные события.|Прошлое|Настоящее|Будущее|Сохранённые партнёры|Отправь имя и знак: Саша / aries|Как тебя называть? Отправь имя до 40 символов 💛|Сделаем паузу. Попробуй немного позже 🌿|Конфиденциальность|Мы храним доступные боту поля Telegram, введённые данные рождения, прогнозы и обращения. Их видят администраторы; при настройке они отправляются в закрытый журнал команды. Мы не видим номер телефона или личные чаты. /delete_me удаляет локальные личные записи и запрашивает удаление сохранённых копий журнала; ограничения Telegram и старые резервные копии могут помешать полному удалению. Данные рождения отправляются API для расчёта планет; перевод получает лишь общедоступный текст.|Короткая помощь|Сохрани дату рождения, выбери время и включи рассылку. Поддержка: /support, история: /history, звёзды: /rewards, остановка: /stop.|🎂 {name}, с днём рождения! Рады, что ты с нами 💛|Команда видит профиль и активность для поддержки и управления. Подробнее: /privacy.|Прогноз дня + запись настроения|Заглянуть три дня на этой неделе|Звёзды — бесплатные внутренние баллы без денежной стоимости.""",
    "he": """💬 פנייה לצוות|ספרו לנו מה מעסיק אתכם בהודעה אחת, עד 1800 תווים. אפשר לצרף תמונה, הודעה קולית או קובץ. ליציאה /cancel.|ההודעה התקבלה 💌 פנייה #{id}. נענה כאן.|💌 תשובת צוות Falino · #{id}|הפניות שלי|הפנייה נסגרה. לפנייה חדשה: /support.|עדיין אין כאן כלום 🌱|היסטוריית הקריאות שלי|המועדפים שלי|⭐ שמירה|הסרה מהמועדפים|הקריאה עזרה לכם?|תודה על המשוב 💛|תודה, נמשיך להשתפר 🌿|רצף הביקורים שלי|המשימות הקטנות שלי|הכוכבים שלי|קבלת כוכבי היום|הפרס הזה כבר התקבל ✨|כוכבים|ימים|אוסף הטארוט שלי|שלושה קלפי טארוט|פריסה משעשעת על עבר, הווה ועתיד; המשמעויות מגיעות מהקלפים ואינן חיזוי אירועים.|עבר|הווה|עתיד|חברים שמורים|שלחו כינוי ומזל, למשל: דני / aries|איך לקרוא לכם? שלחו שם עד 40 תווים 💛|ניקח הפסקה קצרה. נסו שוב בהמשך 🌿|פרטיות והנתונים שלי|נשמור את פרטי Telegram הזמינים לבוט, פרטי לידה שתזינו, קריאות והודעות תמיכה. מנהלים יכולים לצפות בהם; אם הוגדר, הם נשלחים ליומן הצוות הפרטי. איננו רואים מספר טלפון או שיחות פרטיות. /delete_me מוחק נתונים אישיים מקומיים ומבקש למחוק עותקי יומן מתועדים; מגבלות Telegram או גיבויים ישנים עלולים למנוע מחיקה מלאה. פרטי לידה נשלחים לממשק לחישוב כוכבי לכת; תרגום מקבל רק טקסט ציבורי.|עזרה קצרה|שמרו תאריך לידה, בחרו שעה והפעילו משלוח יומי. תמיכה /support, היסטוריה /history, כוכבים /rewards, עצירה /stop.|🎂 {name}, יום הולדת שמח! שמחים שאתם איתנו 💛|הצוות יכול לצפות בפרופיל ובפעילות לצורך תמיכה וניהול. פרטים: /privacy.|קריאה יומית + תיעוד מצב רוח|ביקור בשלושה ימים השבוע|כוכבים הם נקודות חינמיות בבוט ללא ערך כספי או דרישת תשלום.""",
    "es": """💬 Hablar con el equipo|Cuéntanos qué tienes en mente en un mensaje de hasta 1800 caracteres. Puedes adjuntar foto, audio o archivo. Para salir: /cancel.|Recibimos tu mensaje 💌 Ticket #{id}. Te responderemos aquí.|💌 Respuesta del equipo Falino · #{id}|Mis tickets|Este ticket está cerrado. Abre uno nuevo con /support.|Aún no hay nada aquí 🌱|Mi historial|Mis favoritos|⭐ Guardar|Quitar de favoritos|¿Te gustó la lectura?|Gracias por tu opinión 💛|Gracias, seguiremos mejorando 🌿|Mi racha diaria|Mis pequeños retos|Mis estrellas|Recoger estrellas de hoy|Ya recibiste esta recompensa ✨|Estrellas|Días|Mi colección de tarot|Tarot de tres cartas|Tirada lúdica de pasado, presente y futuro; los significados vienen de las cartas, no son predicciones de sucesos.|Pasado|Presente|Futuro|Amigos guardados|Envía un nombre y signo: Alex / aries|¿Cómo te llamamos? Envía un nombre de hasta 40 caracteres 💛|Hagamos una pausa. Prueba de nuevo en un momento 🌿|Privacidad y mis datos|Guardamos los campos de Telegram disponibles para el bot, los datos de nacimiento que introduces, lecturas y mensajes de soporte. Los administradores pueden verlos y, si se configura, se envían al registro privado del equipo. No vemos tu teléfono ni chats privados. /delete_me borra datos personales locales y solicita borrar copias del registro; límites de Telegram o copias antiguas pueden impedir borrarlos por completo. Los datos de nacimiento van a la API para calcular planetas; la traducción recibe solo texto público.|Ayuda rápida|Guarda tu fecha, elige hora y activa los mensajes diarios. Soporte /support, historial /history, estrellas /rewards, detener /stop.|🎂 ¡Feliz cumpleaños, {name}! Qué alegría tenerte aquí 💛|El equipo puede ver tu perfil y actividad para soporte y gestión. Detalles: /privacy.|Lectura diaria + ánimo|Visitarnos tres días esta semana|Las estrellas son puntos gratis del bot, sin valor monetario ni pago.""",
    "fr": """💬 Parler à l’équipe|Dis-nous ce qui te préoccupe en un message de 1800 caractères maximum. Photo, message vocal ou fichier possibles. Pour quitter : /cancel.|Message reçu 💌 Ticket #{id}. Notre réponse arrivera ici.|💌 Réponse de l’équipe Falino · #{id}|Mes tickets|Ce ticket est fermé. Ouvre-en un autre avec /support.|Rien ici pour le moment 🌱|Mon historique|Mes favoris|⭐ Garder|Retirer des favoris|Cette lecture t’a plu ?|Merci pour ton avis 💛|Merci, on continue à améliorer 🌿|Ma série quotidienne|Mes petits défis|Mes étoiles|Récupérer les étoiles du jour|Tu as déjà reçu cette récompense ✨|Étoiles|Jours|Ma collection de tarot|Tarot à trois cartes|Tirage ludique passé, présent et futur ; les significations viennent des cartes, sans prédire des événements réels.|Passé|Présent|Futur|Amis enregistrés|Envoie un prénom et un signe : Alex / aries|Comment t’appeler ? Envoie un prénom de 40 caractères maximum 💛|Faisons une petite pause. Réessaie bientôt 🌿|Confidentialité et données|Nous gardons les champs Telegram accessibles au bot, les détails de naissance saisis, les lectures et les messages d’aide. Les administrateurs les voient et, si configuré, ils sont envoyés au journal privé de l’équipe. Nous ne voyons ni téléphone ni chats privés. /delete_me supprime les données personnelles locales et demande la suppression des copies suivies ; les limites Telegram ou d’anciennes sauvegardes peuvent empêcher leur effacement complet. Les détails de naissance sont envoyés à l’API pour les calculs planétaires ; la traduction reçoit seulement du texte public.|Aide rapide|Enregistre ta naissance, choisis une heure et active l’envoi quotidien. Aide /support, historique /history, étoiles /rewards, arrêt /stop.|🎂 Joyeux anniversaire, {name} ! Heureux de te retrouver ici 💛|L’équipe peut voir ton profil et ton activité pour l’aide et la gestion. Détails : /privacy.|Lecture du jour + humeur|Passer trois jours cette semaine|Les étoiles sont des points gratuits du bot, sans valeur monétaire ni paiement.""",
    "tr": """💬 Ekiple konuş|Aklındakini tek mesajda, en fazla 1800 karakterle anlat. Fotoğraf, ses veya dosya ekleyebilirsin. Çıkış: /cancel.|Mesajın geldi 💌 Talep #{id}. Yanıtımız buraya gelecek.|💌 Falino ekibinden yanıt · #{id}|Destek taleplerim|Bu talep kapalı. Yenisi için /support.|Henüz bir şey yok 🌱|Yorum geçmişim|Favorilerim|⭐ Kaydet|Favorilerden kaldır|Yorumu beğendin mi?|Görüşün için teşekkürler 💛|Teşekkürler, geliştirmeye devam 🌿|Günlük serim|Küçük görevlerim|Yıldızlarım|Bugünün yıldızlarını al|Bu ödülü zaten aldın ✨|Yıldız|Gün|Tarot koleksiyonum|Üç kart tarot|Geçmiş, şimdi ve gelecek için eğlencelik açılım; anlamlar kartlardan gelir, gerçek olay tahmini değildir.|Geçmiş|Şimdi|Gelecek|Kayıtlı arkadaşlar|Bir ad ve burç gönder: Deniz / aries|Sana ne diyelim? En fazla 40 karakterlik ad gönder 💛|Küçük bir mola verelim. Biraz sonra tekrar dene 🌿|Gizlilik ve verilerim|Botun erişebildiği Telegram profil alanlarını, girdiğin doğum bilgilerini, yorumları ve destek mesajlarını saklarız. Yöneticiler görebilir; ayarlanırsa özel ekip günlüğüne gönderilir. Telefonunu veya özel sohbetlerini göremeyiz. /delete_me yerel kişisel kayıtları siler ve izlenen günlük kopyalarının silinmesini ister; Telegram sınırları veya eski yedekler tam silinmeyi engelleyebilir. Gezegen hesabı için doğum bilgileri API’ye gider; çeviriye yalnızca genel yorum metni gönderilir.|Hızlı yardım|Doğum tarihini kaydet, saat seç ve günlük gönderimi aç. Destek /support, geçmiş /history, yıldızlar /rewards, durdurma /stop.|🎂 İyi ki doğdun {name}! Burada olmana çok sevindik 💛|Destek ve yönetim için ekip profilini ve yorum etkinliğini görebilir. Ayrıntılar: /privacy.|Günlük yorum + ruh hali|Bu hafta üç gün uğra|Yıldızlar ücretsiz bot içi puanlardır; nakit değeri veya ödeme zorunluluğu yoktur.""",
}


def install(texts):
    for lang, block in BASE.items():
        texts[lang] = dict(line.split("=", 1) for line in block.strip().splitlines())
        texts[lang]["help"] = texts["en"]["help"]
    for lang, row in EXTRA.items():
        # Delimiters in examples are written as '/', so each row has fixed width.
        values = row.split("|")
        if lang == "en" and len(values) == len(EXTRA_KEYS) + 1:
            # The English example contains a literal pipe; normalize it once.
            index = EXTRA_KEYS.index("partner_prompt")
            values[index : index + 2] = [values[index] + "/" + values[index + 1]]
        assert len(values) == len(EXTRA_KEYS), (lang, len(values), len(EXTRA_KEYS))
        texts[lang].update(dict(zip(EXTRA_KEYS, values, strict=True)))
    texts["fa"].update(
        {
            "welcome": "سلام رفیق ✨ به فالینو خوش اومدی!\nیه گوشه دنج برای فال، حال خوب و چند دقیقه وقت برای خودت 💛\nدوست داری از کجا شروع کنیم؟",
            "daily": "🔮 فال امروز من",
            "weekly": "🌿 حال‌وهوای این هفته",
            "monthly": "🌙 مسیر این ماه",
            "yearly": "✨ نگاه به امسال",
            "birth": "🎂 تولدم رو ثبت کنم",
            "profile": "👤 دنیای من",
            "saved": "حله، برات نگهش داشتم ✅",
            "error": "سرویس یه کم خسته شده 🌿 چند دقیقه دیگه دوباره سر بزن.",
            "choose": "برجت رو انتخاب کن ✨ اگه مطمئن نیستی، از بخش تولد کمکت می‌کنم.",
            "birth_prompt": "تاریخ تولدت رو به ترتیب سال-ماه-روز بفرست 🎂\nشمسی مثل ۱۳۷۴-۰۱-۲۳، میلادی مثل 1995-04-12.",
        }
    )
    for lang in texts:
        texts[lang]["help"] += (
            " /support /tickets /history /favorites /rewards /quests /streak /collection /spread /partners /name /faq /privacy"
        )

    explore = {
        "fa": "✨ بیشتر کشف کنیم",
        "en": "✨ Explore more",
        "ar": "✨ اكتشف المزيد",
        "zh": "✨ 探索更多",
        "hi": "✨ और खोजें",
        "ru": "✨ Больше возможностей",
        "he": "✨ לגלות עוד",
        "es": "✨ Explorar más",
        "fr": "✨ Explorer encore",
        "tr": "✨ Daha fazlası",
    }
    for lang, label in explore.items():
        texts[lang]["explore"] = label

    fraud_notice = {
        "fa": " شمارنده‌های تجمیعی و توکن رمزنگاری‌شده جلوگیری از تکرار جذب و جایزه، پس از حذف پروفایل باقی می‌مانند؛ نام یا شناسه خام در این توکن ذخیره نمی‌شود.",
        "en": " Aggregate counters and keyed anti-abuse fingerprints remain after profile deletion to prevent repeated acquisition credits and referral rewards; the fingerprints contain no raw name or ID.",
        "ar": " تبقى العدادات الإجمالية وبصمات منع التكرار المشفرة بعد حذف الملف لمنع تكرار احتساب الانضمام والمكافآت؛ دون اسم أو معرّف خام.",
        "zh": " 删除资料后，汇总计数和带密钥的防重复指纹会保留，以防重复计算拉新和邀请奖励；指纹中不保存原始姓名或账号 ID。",
        "hi": " प्रोफ़ाइल हटने के बाद कुल काउंटर और keyed दुरुपयोग-रोधी फिंगरप्रिंट रहते हैं, ताकि सदस्यता और रेफ़रल इनाम दोबारा न गिने जाएँ; इनमें मूल नाम या ID नहीं होता।",
        "ru": " После удаления сохраняются агрегированные счётчики и ключевые отпечатки против повторного зачёта привлечения и наград; без исходного имени или ID.",
        "he": " לאחר מחיקה נשמרים מונים מצטברים וטביעות מוגנות מפתח למניעת ספירה ופרסי הזמנה כפולים; ללא שם או מזהה גולמי.",
        "es": " Tras borrar el perfil se conservan contadores agregados y huellas con clave contra créditos y recompensas duplicadas, sin nombre ni ID sin procesar.",
        "fr": " Après suppression restent les compteurs agrégés et empreintes à clé contre les crédits et récompenses répétés, sans nom ni identifiant brut.",
        "tr": " Profil silinse de yinelenen katılım ve davet ödüllerini önlemek için toplam sayaçlar ve anahtarlı parmak izleri kalır; ham ad veya kimlik içermez.",
    }
    for lang, notice in fraud_notice.items():
        texts[lang]["privacy_text"] += notice

    labels = {
        "fa": (
            "باز",
            "بسته",
            "تو",
            "تیم فالینو",
            "رکورد",
            "دوستت وقتی تاریخ تولدش را کامل کند و اولین فال روزانه را بگیرد، ۳۰ ستاره برایت ثبت می‌شود؛ هر حساب فقط یک‌بار.",
        ),
        "en": (
            "Open",
            "Closed",
            "You",
            "Falino team",
            "Best streak",
            "Earn 30 stars when an invited friend completes their birth profile and receives a daily reading. Each account qualifies once.",
        ),
        "ar": (
            "مفتوحة",
            "مغلقة",
            "أنت",
            "فريق فالينو",
            "أفضل سلسلة",
            "احصل على 30 نجمة عندما يكمل صديقك بيانات ميلاده ويتلقى أول قراءة يومية؛ مرة واحدة لكل حساب.",
        ),
        "zh": (
            "处理中",
            "已关闭",
            "你",
            "Falino 团队",
            "最高纪录",
            "邀请的朋友填写完整生日并收到首次每日运势后，你可获得 30 颗星星；每个账号只计一次。",
        ),
        "hi": (
            "खुला",
            "बंद",
            "आप",
            "Falino टीम",
            "सबसे लंबी श्रृंखला",
            "दोस्त जन्म प्रोफ़ाइल पूरी करके पहला दैनिक राशिफल पाए, तो आपको 30 सितारे मिलते हैं। हर खाते पर एक बार।",
        ),
        "ru": (
            "Открыто",
            "Закрыто",
            "Вы",
            "Команда Falino",
            "Лучшая серия",
            "Получи 30 звёзд, когда приглашённый друг заполнит дату рождения и получит дневной прогноз. Один раз на аккаунт.",
        ),
        "he": (
            "פתוח",
            "סגור",
            "אתם",
            "צוות Falino",
            "שיא הרצף",
            "תקבלו 30 כוכבים כשחבר מוזמן ישלים פרטי לידה ויקבל קריאה יומית. פעם אחת לכל חשבון.",
        ),
        "es": (
            "Abierto",
            "Cerrado",
            "Tú",
            "Equipo Falino",
            "Mejor racha",
            "Ganas 30 estrellas cuando un amigo invitado completa su fecha de nacimiento y recibe su primera lectura diaria. Una vez por cuenta.",
        ),
        "fr": (
            "Ouvert",
            "Fermé",
            "Toi",
            "Équipe Falino",
            "Meilleure série",
            "Gagne 30 étoiles quand un ami invité complète sa date de naissance et reçoit sa première lecture du jour. Une fois par compte.",
        ),
        "tr": (
            "Açık",
            "Kapalı",
            "Sen",
            "Falino ekibi",
            "En iyi seri",
            "Davet ettiğin arkadaş doğum profilini tamamlayıp ilk günlük yorumunu aldığında 30 yıldız kazanırsın. Hesap başına bir kez.",
        ),
    }
    for lang, row in labels.items():
        texts[lang].update(
            dict(
                zip(
                    ("ticket_open_label", "ticket_closed_label", "role_user", "role_staff", "record", "referral_note"),
                    row,
                    strict=True,
                )
            )
        )
    for lang in texts:
        texts[lang]["rewards"] = texts[lang]["reward"]
