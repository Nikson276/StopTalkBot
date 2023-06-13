'''All SQL query definition here in Constants'''

GROUP_ID: str = "SELECT `id` FROM `group_settings` WHERE `group_id` = ?"
SETTINGS: str = ("SELECT `mode`, `video_hate` "
                 "FROM `group_settings` WHERE `id` = ?"
                 )
RATING_ID: str = "SELECT `id` FROM `rating_board` WHERE `group_id` = ?"
RATING_ID_FULL: str = ("SELECT `id` FROM `rating_board` "
                       "WHERE `group_id` = ? AND `user_id` = ?"
                       )
RATING_RECORD: str = "SELECT * FROM `rating_board` WHERE `group_id` = ?"
RATING_VALUE: str = ("SELECT `voice_score`, `video_score` "
                     "FROM `rating_board` WHERE `id` = ?"
                     )

UPD_GROUP: str = ("UPDATE `group_settings` "
                  "SET `mode` = ?, `video_hate` = ? WHERE `id` = ?"
                  )
INS_GROUP: str = "INSERT INTO `group_settings` (`group_id`) VALUES (?)"
UPD_RATING_VOICE: str = ("UPDATE `rating_board` "
                         "SET `voice_score` = ? WHERE `id` = ?"
                         )
UPD_RATING_VIDEO: str = ("UPDATE `rating_board` "
                         "SET `video_score` = ? WHERE `id` = ?"
                         )
INS_RATING_VOICE: str = ("INSERT INTO `rating_board` "
                         "(`group_id`, `user_id`, `voice_score`) "
                         "VALUES (?,?,?)"
                         )
INS_RATING_VIDEO: str = ("INSERT INTO `rating_board` "
                         "(`group_id`, `user_id`, `video_score`) "
                         "VALUES (?,?,?)"
                         )
DEL_GROUP: str = "DELETE FROM `group_settings` WHERE `id` = ?"
DEL_RATING: str = "DELETE FROM `rating_board` WHERE `id` = ?"
