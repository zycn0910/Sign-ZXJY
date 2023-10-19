import datetime

import config
import pushinfo


class MessagePush:
    @staticmethod
    def pushMessage(addinfo=True, pushmode=None, title="默认标题", content="默认内容", pushdata=None):
        if addinfo:
            if pushmode == "1":
                if pushdata['Ding']['Secret'] or pushdata['Ding']['Token'] is not None:
                    feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                      DingToken=pushdata['Ding']['Token'], title=title,
                                                      content=content)
                else:
                    feedback = pushinfo.DingTalkRebot(DingSecret=config.DingDingSecret,
                                                      DingToken=config.DingDingSecret, title=title,
                                                      content=content)
                return feedback
            elif pushmode == "2":
                if pushdata['PushPlus']['Token'] is not None:
                    feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                else:
                    feedback = pushinfo.PushPlus(token=config.PushPlusToken, title=title, content=content)
                return feedback
            elif pushmode == "3":
                if pushdata['Server_Turbo']['Token'] is not None:
                    feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title,
                                                    content=content)
                else:
                    feedback = pushinfo.ServerTurbo(token=config.Server_Turbo, title=title, content=content)
                return feedback
            elif pushmode == "4":
                if pushdata['Email']['Send'] or pushdata['Email']['Password'] or pushdata['Email']['Server_Address'] or \
                        pushdata['Email']['Smtp_Port'] is not None:
                    feedback = pushinfo.Send_Email(Send=pushdata['Email']['Send'],
                                                   Password=pushdata['Email']['Password'],
                                                   Server_Address=pushdata['Email']['Server_Address'],
                                                   Smtp_Port=pushdata['Email']['Smtp_Port'],
                                                   Receiver=pushdata['Email']['Receiver'], title=title, content=content)
                else:
                    feedback = pushinfo.Send_Email(Send=config.email_username,
                                                   Password=config.email_password,
                                                   Server_Address=config.email_address,
                                                   Smtp_Port=config.email_port,
                                                   Receiver=pushdata['Email']['Receiver'], title=title, content=content)
                return feedback
            else:
                feedback = title + "\n" + content
                return feedback
        else:
            if config.time == datetime.datetime.now().strftime("%H") or config.time == "":
                if pushmode == "1":
                    if pushdata['Ding']['Secret'] or pushdata['Ding']['Token'] is not None:
                        feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                          DingToken=pushdata['Ding']['Token'], title=title,
                                                          content=content)
                    else:
                        feedback = pushinfo.DingTalkRebot(DingSecret=config.DingDingSecret,
                                                          DingToken=config.DingDingToken, title=title,
                                                          content=content)
                    return feedback
                elif pushmode == "2":
                    if pushdata['PushPlus']['Token'] is not None:
                        feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                    else:
                        feedback = pushinfo.PushPlus(token=config.PushPlusToken, title=title, content=content)
                    return feedback
                elif pushmode == "3":
                    if pushdata['Server_Turbo']['Token'] is not None:
                        feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title,
                                                        content=content)
                    else:
                        feedback = pushinfo.ServerTurbo(token=config.Server_Turbo, title=title, content=content)
                    return feedback
                elif pushmode == "4":
                    if config.email_username or config.email_password or config.email_address or config.email_port == "":
                        feedback = pushinfo.Send_Email(Send=config.email_username,
                                                       Password=config.email_password,
                                                       Server_Address=config.email_address,
                                                       Smtp_Port=config.email_port,
                                                       Receiver=pushdata['Email']['Receiver'], title=title,
                                                       content=content)

                    else:
                        feedback = pushinfo.Send_Email(Send=pushdata['Email']['Send'],
                                                       Password=pushdata['Email']['Password'],
                                                       Server_Address=pushdata['Email']['Server_Address'],
                                                       Smtp_Port=pushdata['Email']['Smtp_Port'],
                                                       Receiver=pushdata['Email']['Receiver'], title=title,
                                                       content=content)
                    return feedback
                else:
                    feedback = title + "\n" + content
                    return feedback
            else:
                feedback = f"未在推送时效！"
                return feedback
