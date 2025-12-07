// CodeMirror Markdown工具栏插件
(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["codemirror"], mod);
  else // Plain browser env
    mod(window.CodeMirror || CodeMirror);
})(function(CodeMirror) {
  "use strict";

  var markdownToolbar = {
    // 插入图片
    insertImage: function(cm) {
      var selection = cm.getSelection();
      var text = selection || "图片描述";
      var url = prompt("请输入图片URL:", "");
      if (url) {
        cm.replaceSelection("![" + text + "](" + url + ")");
      }
    },
    
    // 插入代码块
    insertCodeBlock: function(cm) {
      var selection = cm.getSelection();
      var lang = prompt("请输入代码语言(可选):", "");
      cm.replaceSelection("```" + (lang || "") + "\n" + (selection || "代码内容") + "\n```");
    },
    
    // 插入行内代码
    insertInlineCode: function(cm) {
      var selection = cm.getSelection() || "代码";
      cm.replaceSelection("`" + selection + "`");
    },
    
    // 插入链接
    insertLink: function(cm) {
      var selection = cm.getSelection() || "链接文本";
      var url = prompt("请输入链接URL:", "");
      if (url) {
        cm.replaceSelection("[" + selection + "](" + url + ")");
      }
    },
    
    // 插入表格
    insertTable: function(cm) {
      var rows = prompt("请输入表格行数:", "3");
      var cols = prompt("请输入表格列数:", "3");
      
      if (rows && cols) {
        rows = parseInt(rows);
        cols = parseInt(cols);
        
        var table = "";
        
        // 表头
        table += "|";
        for (var i = 0; i < cols; i++) {
          table += " 表头" + (i + 1) + " |";
        }
        table += "\n";
        
        // 分隔线
        table += "|";
        for (var i = 0; i < cols; i++) {
          table += " --- |";
        }
        table += "\n";
        
        // 数据行
        for (var i = 0; i < rows - 1; i++) {
          table += "|";
          for (var j = 0; j < cols; j++) {
            table += " 数据 |";
          }
          table += "\n";
        }
        
        cm.replaceSelection(table);
      }
    },
    
    // 插入标题
    insertHeader: function(cm, level) {
      level = level || 1;
      var selection = cm.getSelection() || "标题";
      cm.replaceSelection("#".repeat(level) + " " + selection);
    },
    
    // 插入列表
    insertList: function(cm, ordered) {
      var selection = cm.getSelection();
      var lines = selection ? selection.split("\n") : [""];
      
      for (var i = 0; i < lines.length; i++) {
        lines[i] = (ordered ? (i + 1) + ". " : "- ") + lines[i];
      }
      
      cm.replaceSelection(lines.join("\n"));
    },
    
    // 插入引用
    insertBlockquote: function(cm) {
      var selection = cm.getSelection() || "引用内容";
      var lines = selection.split("\n");
      
      for (var i = 0; i < lines.length; i++) {
        lines[i] = "> " + lines[i];
      }
      
      cm.replaceSelection(lines.join("\n"));
    },
    
    // 插入水平线
    insertHorizontalRule: function(cm) {
      cm.replaceSelection("\n---\n");
    },
    
    // 插入粗体
    insertBold: function(cm) {
      var selection = cm.getSelection() || "粗体文本";
      cm.replaceSelection("**" + selection + "**");
    },
    
    // 插入斜体
    insertItalic: function(cm) {
      var selection = cm.getSelection() || "斜体文本";
      cm.replaceSelection("*" + selection + "*");
    },
    
    // 插入删除线
    insertStrikethrough: function(cm) {
      var selection = cm.getSelection() || "删除线文本";
      cm.replaceSelection("~~" + selection + "~~");
    }
  };

  CodeMirror.defineOption("markdownToolbar", false, function(cm) {
    cm.markdownToolbar = markdownToolbar;
  });

  // 命令
  CodeMirror.commands.insertImage = function(cm) {
    markdownToolbar.insertImage(cm);
  };
  
  CodeMirror.commands.insertCodeBlock = function(cm) {
    markdownToolbar.insertCodeBlock(cm);
  };
  
  CodeMirror.commands.insertInlineCode = function(cm) {
    markdownToolbar.insertInlineCode(cm);
  };
  
  CodeMirror.commands.insertLink = function(cm) {
    markdownToolbar.insertLink(cm);
  };
  
  CodeMirror.commands.insertTable = function(cm) {
    markdownToolbar.insertTable(cm);
  };
  
  CodeMirror.commands.insertHeader1 = function(cm) {
    markdownToolbar.insertHeader(cm, 1);
  };
  
  CodeMirror.commands.insertHeader2 = function(cm) {
    markdownToolbar.insertHeader(cm, 2);
  };
  
  CodeMirror.commands.insertHeader3 = function(cm) {
    markdownToolbar.insertHeader(cm, 3);
  };
  
  CodeMirror.commands.insertUnorderedList = function(cm) {
    markdownToolbar.insertList(cm, false);
  };
  
  CodeMirror.commands.insertOrderedList = function(cm) {
    markdownToolbar.insertList(cm, true);
  };
  
  CodeMirror.commands.insertBlockquote = function(cm) {
    markdownToolbar.insertBlockquote(cm);
  };
  
  CodeMirror.commands.insertHorizontalRule = function(cm) {
    markdownToolbar.insertHorizontalRule(cm);
  };
  
  CodeMirror.commands.insertBold = function(cm) {
    markdownToolbar.insertBold(cm);
  };
  
  CodeMirror.commands.insertItalic = function(cm) {
    markdownToolbar.insertItalic(cm);
  };
  
  CodeMirror.commands.insertStrikethrough = function(cm) {
    markdownToolbar.insertStrikethrough(cm);
  };
});