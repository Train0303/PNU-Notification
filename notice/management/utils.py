mail_error_code = {
    450: ["4.7.1 MMCNT IP ADDRESS: Message refused. Your IP address has sent too many mails."],
    550: ['5.1.1 MUSR IP ADDRESS: No such user: RECIPIENT ADDRESS',
          '5.1.1 RUSR IP ADDRESS: No such user: RECIPIENT ADDRESS',
          '5.2.1 DDENY IP ADDRESS : The receiver denied your mail. Please contact the receiver with another way.',
          '5.2.1 RBLK IP ADDRESS: Mailbox is blocked: RECIPIENT ADDRESS',
          '5.7.1 RDENY IP ADDRESS : The receiver denied your mail. Please contact the receiver with another way.'],
    553: ['5.1.7 MADDR IP ADDRESS: Invalid mail address: SENDER ADDRESS']
}