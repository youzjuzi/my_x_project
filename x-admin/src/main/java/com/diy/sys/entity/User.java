package com.diy.sys.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.List;

/**
 * <p>
 * 
 * </p>
 *
 * @author youzi
 * @since 2023-09-02
 */
@Data
@TableName("x_user")
@AllArgsConstructor
@NoArgsConstructor
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    @TableId(value = "id", type = IdType.AUTO)
    private Integer id;
    private String username;
    private String password;
    private String email;
    private String phone;
    private Integer status;
    private String avatar;
    private Integer deleted;
    @TableField(exist = false)
    private String captcha;
    @TableField(exist = false)
    private String codeKey;
    @TableField(exist = false)
    private List<Integer> roleIdList;
}
