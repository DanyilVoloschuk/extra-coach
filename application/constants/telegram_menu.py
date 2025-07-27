from domain.constants import chat_constants


SAY_WHAT_EAT_TEXT = "🗣 скажи шо жер"
CAPTURE_WHAT_EAT_TEXT = "📸 Сфоткай шо жер"
WRITE_WHAT_EAT_TEXT = "✍️ Напиши шо жер"

ACTIVITY_TO_DOMAIN_STAGE = {
    SAY_WHAT_EAT_TEXT: chat_constants.AWAITING_FOR_AUDIO_FOOD,
    CAPTURE_WHAT_EAT_TEXT: chat_constants.AWAITING_FOR_PHOTO_FOOD,
    WRITE_WHAT_EAT_TEXT: chat_constants.AWAITING_FOR_TEXT_FOOD,
}

ACTIVITY_MENU = [
    SAY_WHAT_EAT_TEXT,
    CAPTURE_WHAT_EAT_TEXT,
    WRITE_WHAT_EAT_TEXT,
]

START_NEW_DAY_TEXT = "🌞 Почати новий день"

PROFILE_TEXT = "👤 Профіль"
EAT_STATS_TEXT = "🎥 переглянь шо жер"

GIVE_MONEY_TEXT = "🤑🤑🤑🤑дать дєнєг🤑🤑🤑🤑"
HELP_TEXT = "❓ допомога"

DEFAULT_MENU = [
    ACTIVITY_MENU,
    [START_NEW_DAY_TEXT],
    [PROFILE_TEXT, EAT_STATS_TEXT],
    [HELP_TEXT]
]