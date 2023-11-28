import datetime
import yaml
import pushinfo


class MessagePush:
    @staticmethod
    def pushMessage(addinfo=True, pushmode=None, title="默认标题", content="默认内容", pushdata=None):
        with open('config.yml', 'r', encoding='utf-8') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)
        if addinfo:
            if pushmode == "1":
                if pushdata['Ding']['Secret'] or pushdata['Ding']['Token'] != "":
                    feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                      DingToken=pushdata['Ding']['Token'], title=title,
                                                      content=content)
                else:
                    feedback = pushinfo.DingTalkRebot(DingSecret=config['push-data']['DingDing']['Secret'],
                                                      DingToken=config['push-data']['DingDing']['Token'], title=title,
                                                      content=content)
                return feedback
            elif pushmode == "2":
                if pushdata['PushPlus']['Token'] != "":
                    feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                else:
                    feedback = pushinfo.PushPlus(token=config['push-data']['PushPlus']['Token'], title=title, content=content)
                return feedback
            elif pushmode == "3":
                if pushdata['Server_Turbo']['Token'] != "":
                    feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title,
                                                    content=content)
                else:
                    feedback = pushinfo.ServerTurbo(token=config['push-data']['Server_Turbo']['Token'], title=title, content=content)
                return feedback
            elif pushmode == "4":
                if pushdata['Email']['Password'] != "":
                    feedback = pushinfo.Send_Email(Send=pushdata['Email']['Send'],
                                                   Password=pushdata['Email']['Password'],
                                                   Server_Address=pushdata['Email']['Server_Address'],
                                                   Smtp_Port=pushdata['Email']['Smtp_Port'],
                                                   Receiver=pushdata['Email']['Receiver'], title=title, content=content)
                else:
                    feedback = pushinfo.Send_Email(Send=config['push-data']['Email']['email_username'],
                                                   Password=config['push-data']['Email']['email_password'],
                                                   Server_Address=config['push-data']['Email']['email_address'],
                                                   Smtp_Port=config['push-data']['Email']['email_port'],
                                                   Receiver=pushdata['Email']['Receiver'], title=title, content=content)
                return feedback
            else:
                feedback = title + "\n" + content
                return feedback
        else:
            if config['time'] == datetime.datetime.now().strftime("%H") or config['time'] == "":
                if pushmode == "1":
                    if pushdata['Ding']['Secret'] or pushdata['Ding']['Token'] != "":
                        feedback = pushinfo.DingTalkRebot(DingSecret=pushdata['Ding']['Secret'],
                                                          DingToken=pushdata['Ding']['Token'], title=title,
                                                          content=content)
                    else:
                        feedback = pushinfo.DingTalkRebot(DingSecret=config['push-data']['DingDing']['Secret'],
                                                          DingToken=config['push-data']['DingDing']['Token'], title=title,
                                                          content=content)
                    return feedback
                elif pushmode == "2":
                    if pushdata['PushPlus']['Token'] != "":
                        feedback = pushinfo.PushPlus(token=pushdata['PushPlus']['Token'], title=title, content=content)
                    else:
                        feedback = pushinfo.PushPlus(token=config['push-data']['PushPlus']['Token'], title=title, content=content)
                    return feedback
                elif pushmode == "3":
                    if pushdata['Server_Turbo']['Token'] != "":
                        feedback = pushinfo.ServerTurbo(token=pushdata['Server_Turbo']['Token'], title=title,
                                                        content=content)
                    else:
                        feedback = pushinfo.ServerTurbo(token=config['push-data']['Server_Turbo']['Token'], title=title, content=content)
                    return feedback
                elif pushmode == "4":
                    if pushdata['Email']['Password'] != "":
                        feedback = pushinfo.Send_Email(Send=pushdata['Email']['Send'],
                                                       Password=pushdata['Email']['Password'],
                                                       Server_Address=pushdata['Email']['Server_Address'],
                                                       Smtp_Port=pushdata['Email']['Smtp_Port'],
                                                       Receiver=pushdata['Email']['Receiver'], title=title,
                                                       content=content)
                    else:
                        feedback = pushinfo.Send_Email(Send=config['push-data']['Email']['email_username'],
                                                       Password=config['push-data']['Email']['email_password'],
                                                       Server_Address=config['push-data']['Email']['email_address'],
                                                       Smtp_Port=config['push-data']['Email']['email_port'],
                                                       Receiver=pushdata['Email']['Receiver'], title=title,
                                                       content=content)
                    return feedback
                else:
                    feedback = title + "\n" + content
                    return feedback
            else:
                feedback = f"未在推送时效！"
                return feedback
