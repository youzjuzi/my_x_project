package com.diy.sys.entity.MenuAndRole;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Data;

import java.io.Serializable;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * <p>
 * 
 * </p>
 *
 * @author youzi
 * @since 2023-11-08
 */
@TableName("x_menu")
@Data
public class Menu implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "menu_id", type = IdType.AUTO)
    private Integer menuId;
    private String component;
    private String path;
    private String redirect;
    private String name;
    private String title;
    private String icon;
    private Integer parentId;
    private String isLeaf;
    private Boolean hidden;
    @Override
    public String toString() {
        return "Menu{" +
            "menuId = " + menuId +
            ", component = " + component +
            ", path = " + path +
            ", redirect = " + redirect +
            ", name = " + name +
            ", title = " + title +
            ", icon = " + icon +
            ", parentId = " + parentId +
            ", isLeaf = " + isLeaf +
            ", hidden = " + hidden +
        "}";
    }
    @TableField(exist = false)
    @JsonInclude(JsonInclude.Include.NON_EMPTY)
    private List<Menu> children;
    @TableField(exist = false)
    private Map<String,Object> mete;
    public Map<String,Object> getMeta(){
        mete = new HashMap<>();
        mete.put("title",title);
        mete.put("icon",icon);
        return mete;
    }
}
