import {
  Button,
  ButtonGroup,
  DialogActionTrigger,
  Input,
  Text,
  VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaExchangeAlt } from "react-icons/fa"

import { type ApiError, type TacacsUserPublic, TacacsUsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditTacacsUserProps {
  tacacs_user: TacacsUserPublic
}

interface TacacsUserUpdateForm {
  username: string
  password_type: string
  password: string
  member: string
  description?: string
}

const EditTacacsUser = ({ tacacs_user }: EditTacacsUserProps) => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TacacsUserUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      ...tacacs_user,
      description: tacacs_user.description ?? undefined,
      password_type: tacacs_user.password_type ?? undefined,
      password: tacacs_user.password ?? undefined,
      member: tacacs_user.member ?? undefined,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: TacacsUserUpdateForm) =>
      TacacsUsersService.updateTacacsUser({ id: tacacs_user.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("TacacsUser updated successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["tacacs_users"] })
    },
  })

  const onSubmit: SubmitHandler<TacacsUserUpdateForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button variant="ghost">
          <FaExchangeAlt fontSize="16px" />
          Edit TacacsUser
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Edit TacacsUser</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <Text mb={4}>Update the item details below.</Text>
            <VStack gap={4}>
              <Field
                required
                invalid={!!errors.username}
                errorText={errors.username?.message}
                label="username"
              >
                <Input
                  {...register("username", {
                    required: "username is required",
                  })}
                  placeholder="username"
                  type="text"
                  disabled={true}
                />
              </Field>
              <Field
                required
                invalid={!!errors.password_type}
                errorText={errors.password_type?.message}
                label="password_type"
              >
                <Input
                  {...register("password_type", {
                    required: "password_type is required.",
                  })}
                  placeholder="password_type"
                  type="text"
                />
              </Field>
              <Field
                required
                invalid={!!errors.password}
                errorText={errors.password?.message}
                label="password"
              >
                <Input
                  {...register("password", {
                    required: "password is required.",
                  })}
                  placeholder="password"
                  type="password"
                />
              </Field>
              <Field
                required
                invalid={!!errors.member}
                errorText={errors.member?.message}
                label="member"
              >
                <Input
                  {...register("member", {
                    required: "member is required.",
                  })}
                  placeholder="member"
                  type="text"
                />
              </Field>
              <Field
                invalid={!!errors.description}
                errorText={errors.description?.message}
                label="Description"
              >
                <Input
                  {...register("description")}
                  placeholder="Description"
                  type="text"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            <ButtonGroup>
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancel
                </Button>
              </DialogActionTrigger>
              <Button variant="solid" type="submit" loading={isSubmitting}>
                Save
              </Button>
            </ButtonGroup>
          </DialogFooter>
        </form>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  )
}

export default EditTacacsUser
