import datetime

import config
import pushinfo


class MessagePush:
    @staticmethod
    def pushMessage(addinfo=True, pushmode=None, title="默认标题", content="默认内容", pushdata=None):
        if addinfo == True:
            if pushmode == "1":
                feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                  DingToken=pushdata['Ding']['Token'], title=title,
                                                  content=content)
                return feedback
            elif pushmode == "2":
                feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                return feedback
            elif pushmode == "3":
                feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title, content=content)
                return feedback
            elif pushmode == "4":
                if config.email_username or config.email_password or config.email_address or config.email_port == "":
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
                    feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                      DingToken=pushdata['Ding']['Token'], title=title,
                                                      content=content)
                    return feedback
                elif pushmode == "2":
                    feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                    return feedback
                elif pushmode == "3":
                    feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title,
                                                    content=content)
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
