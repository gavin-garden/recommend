CREATE TABLE `video_behavior` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `device` VARCHAR(32) NOT NULL COMMENT '用户设备id',
  `video` VARCHAR(16) NOT NULL COMMENT '视频id',
  `operation` TINYINT NOT NULL COMMENT '操作类型',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  INDEX `ix_device_create` (`device`, `created_at`)
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COMMENT = '用户操作视频的行为';
