;; -*-emacs-lisp-*-
;;
;; Emacs startup file, e.g.  /etc/emacs/site-start.d/50ical2org.el
;; for the Debian ical2org package
;;
;; Originally contributed by Nils Naumann <naumann@unileoben.ac.at>
;; Modified by Dirk Eddelbuettel <edd@debian.org>
;; Adapted for dh-make by Jim Van Zandt <jrv@debian.org>

;; The ical2org package follows the Debian/GNU Linux 'emacsen' policy and
;; byte-compiles its elisp files for each 'emacs flavor' (emacs19,
;; xemacs19, emacs20, xemacs20...).  The compiled code is then
;; installed in a subdirectory of the respective site-lisp directory.
;; We have to add this to the load-path:
(let ((package-dir (concat "/usr/share/"
                           (symbol-name flavor)
                           "/site-lisp/ical2org")))
;; If package-dir does not exist, the ical2org package must have
;; removed but not purged, and we should skip the setup.
  (when (file-directory-p package-dir)
    (setq load-path (cons package-dir load-path))
    (autoload 'ical2org-mode "ical2org-mode"
      "Major mode for editing ical2org files." t)
    (add-to-list 'auto-mode-alist '("\\.ical2org$" . ical2org-mode))))

