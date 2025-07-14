from func.changer import *

path = "files/config.toml"
with open(path, "rb") as f:
    config = tomllib.load(f)

pass_on = config['info']['pass_on']
change = config['info']['change_pass']
sip_pass_on = config['info']['sip']
pass_change = Changer(
    config['info']['login'],
    config['info']['password'],
    config['info']['server'],
    config['info']['domain_name'],
    config['info']['user_list'],
    config['info']['new_password']
)
check = os.path.exists(pass_change.path_user_xlsx)


def main():
    pass_change.logging_setup_and_start()
    pass_change.server_connect()
    pass_change.server_login()
    end_text = "Операции были успешно завершены!"

    def exit_changer():
        pass_change.server.disconnect()
        logging.info('The operations were completed successfully')
        print(end_text)
        sys.exit(0)

    if sip_pass_on == 0 and pass_on == 2 and change == 0:
        end_text = ("В конфигурационном файле установленные параметры не приведут к изменениям.\nВнесите изменения "
                    "в конфигурационный файл")
        exit_changer()

    list_name = list((pass_change.server.list_accounts(pass_change.domain[1:])['body']).keys())
    text = f"1 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена {pass_change.domain}\n"

    if sip_pass_on:
        text += (
            f"2 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена "
            f"{pass_change.domain} и задать сгенерированные SIP пароли\n"
            f"3 - Сгенерировать и задать SIP пароли для аккаунтов домена {pass_change.domain} из "
            f"файла {pass_change.users_xlsx}\n"
            f"4 - Заменить/Создать SIP пароли из файла {pass_change.users_xlsx} аккаунтам домена {pass_change.domain}\n"
        )
    else:
        text += (
            f"2 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена {pass_change.domain} и "
            f"задать пароли\n"
        )
        if check:
            text += (
                f"3 - Использовать существующий файл {pass_change.users_xlsx} с аккаунтами домена {pass_change.domain} "
                f"и задать пароли\n"
            )
    while True:
        option = int(input(text + "Ввод: "))
        if option in (1, 2):
            # creating a xlsx file with users
            if check:
                delete = int(input(
                    f"Файл {pass_change.users_xlsx} уже существует\n"
                    f"1 - Удалить существующий файл и создать новый\n"
                    f"2 - Использовать существующий файл {pass_change.users_xlsx}\n"
                    f"Ввод: "
                ))
                if delete == 1:
                    os.remove(pass_change.path_user_xlsx)
                    pass_change.create_excel(list_name)
            else:
                pass_change.create_excel(list_name)
            if option == 1:
                exit_changer()
            break
        elif (option in (3, 4) and sip_pass_on) or (option == 3 and not sip_pass_on):
            break
        else:
            print("Введено некорректное значение, попробуйте еще раз")

    # reading the xlsx file with users and changing passwords
    file_users = pd.read_excel(pass_change.path_user_xlsx, usecols=[0])
    file_sip_pass = pd.read_excel(pass_change.path_user_xlsx, usecols=[1])

    # read xlsx file with users and change passwords
    if sip_pass_on:
        for acc, password in zip(file_users.values, file_sip_pass.values):
            pass_change.user = acc[0]
            if option in (2, 3):
                pass_change.gen_pass()
                pass_change.set_password(1)
                pass_change.user_pass_dict['UserName'].append(pass_change.user)
                pass_change.user_pass_dict['Password'].append(pass_change.new_password)
            if option == 4:
                pass_change.new_password = str(password[0])
                if pass_change.new_password == 'nan':
                    end_text = "Часть операций было успешно завершено. Подробности в лог-файле"
                    logging.warning(
                        f"The {pass_change.users_xlsx} file doesn't specify a password for the "
                        f"{pass_change.user}{pass_change.domain} account"
                    )
                    continue
                pass_change.set_password(1)
        if option in (2, 3):
            pass_change.add_user_sip_passwords_to_excel()
        exit_changer()
    for acc in file_users.values:
        pass_change.user = acc[0]
        if pass_on == 1:
            pass_change.switch_pass_on()
        if pass_on == 0:
            pass_change.switch_pass_off()
        if change and pass_on != 0:
            if pass_change.get_acc_pass_on_off():
                if pass_change.new_password == 'none':
                    pass_change.gen_pass()
                    pass_change.set_password()
                    pass_change.user_pass_dict['UserName'].append(pass_change.user)
                    pass_change.user_pass_dict['Password'].append(pass_change.new_password)
                    pass_change.new_password = 'none'
                else:
                    pass_change.set_password()
            else:
                end_text = "Часть операций было успешно завершено. Подробности в лог-файле"
                logging.warning(
                    f"The password is disabled for the {pass_change.user}{pass_change.domain} account. "
                    f"Can't changing password"
                )

    if pass_change.new_password == 'none' and change and not sip_pass_on:
        pass_change.add_users_passwords_to_excel()
    if pass_change.new_password != 'none' and not sip_pass_on:
        pass_change.delete_xlsx_sheet()

    exit_changer()


if __name__ == '__main__':
    main()
